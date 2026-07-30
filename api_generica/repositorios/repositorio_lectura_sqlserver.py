"""
repositorio_lectura_sqlserver.py — Repositorio CRUD para SQL Server.

Características de SQL Server:
- Identificadores con [corchetes]
- TOP (n) en lugar de LIMIT
- Esquema por defecto: 'dbo'
- Requiere convertir cadena ODBC a URL de SQLAlchemy
"""

from typing import Any
from datetime import datetime, date, time
from decimal import Decimal
from uuid import UUID
from urllib.parse import quote_plus

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from servicios.abstracciones.i_proveedor_conexion import IProveedorConexion
from servicios.utilidades.encriptacion_bcrypt import encriptar


class RepositorioLecturaSqlServer:
    """Implementación de acceso a datos para SQL Server usando SQLAlchemy async."""

    def __init__(self, proveedor_conexion: IProveedorConexion):
        if proveedor_conexion is None:
            raise ValueError("proveedor_conexion no puede ser None")
        self._proveedor_conexion = proveedor_conexion
        self._engine: AsyncEngine | None = None

    def _convertir_odbc_a_sqlalchemy(self, cadena_odbc: str) -> str:
        """
        Convierte una cadena ODBC a formato URL de SQLAlchemy.
        Si ya tiene formato SQLAlchemy (mssql+...), la retorna tal cual.
        """
        if cadena_odbc.startswith("mssql+"):
            return cadena_odbc
        cadena_encoded = quote_plus(cadena_odbc)
        return f"mssql+aioodbc:///?odbc_connect={cadena_encoded}"

    async def _obtener_engine(self) -> AsyncEngine:
        """Crea el engine de conexión la primera vez, luego lo reutiliza."""
        if self._engine is None:
            cadena = self._proveedor_conexion.obtener_cadena_conexion()
            cadena_sqlalchemy = self._convertir_odbc_a_sqlalchemy(cadena)
            self._engine = create_async_engine(cadena_sqlalchemy, echo=False)
        return self._engine

    # --- Métodos auxiliares para detectar y convertir tipos ---

    async def _detectar_tipo_columna(
        self, nombre_tabla: str, esquema: str, nombre_columna: str
    ) -> str | None:
        """Consulta INFORMATION_SCHEMA para saber el tipo de una columna."""
        sql = text("""
            SELECT DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = :esquema
            AND TABLE_NAME = :tabla
            AND COLUMN_NAME = :columna
        """)
        try:
            engine = await self._obtener_engine()
            async with engine.connect() as conn:
                result = await conn.execute(sql, {
                    "esquema": esquema, "tabla": nombre_tabla, "columna": nombre_columna
                })
                row = result.fetchone()
                return row[0].lower() if row else None
        except Exception:
            return None

    def _convertir_valor(self, valor: str, tipo_destino: str | None) -> Any:
        """Convierte un string al tipo Python que corresponde según la columna."""
        if tipo_destino is None:
            return valor
        try:
            if tipo_destino in ('int', 'bigint', 'smallint', 'tinyint'):
                return int(valor)
            if tipo_destino in ('decimal', 'numeric', 'money', 'smallmoney'):
                return Decimal(valor)
            if tipo_destino in ('float', 'real'):
                return float(valor)
            if tipo_destino == 'bit':
                return valor.lower() in ('true', '1', 'yes', 'si')
            if tipo_destino == 'uniqueidentifier':
                return UUID(valor)
            if tipo_destino == 'date':
                return self._extraer_solo_fecha(valor)
            if tipo_destino in ('datetime', 'datetime2', 'smalldatetime'):
                return datetime.fromisoformat(valor.replace('Z', '+00:00'))
            if tipo_destino == 'time':
                return time.fromisoformat(valor)
            return valor
        except (ValueError, TypeError):
            return valor

    def _extraer_solo_fecha(self, valor: str) -> date:
        """Extrae la parte de fecha de un string ISO."""
        if 'T' in valor:
            return datetime.fromisoformat(valor.replace('Z', '+00:00')).date()
        return date.fromisoformat(valor[:10])

    def _es_fecha_sin_hora(self, valor: str) -> bool:
        """Detecta si un valor tiene formato YYYY-MM-DD (solo fecha)."""
        return len(valor) == 10 and valor.count('-') == 2 and 'T' not in valor

    # --- Operaciones CRUD ---

    async def obtener_filas(
        self, nombre_tabla: str, esquema: str | None = None, limite: int | None = None
    ) -> list[dict[str, Any]]:
        """Obtiene filas de una tabla con TOP (n)."""
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío")

        esquema_final = (esquema or "dbo").strip()
        limite_final = limite or 1000

        # SQL Server usa TOP en lugar de LIMIT
        sql = text(f"SELECT TOP ({limite_final}) * FROM [{esquema_final}].[{nombre_tabla}]")

        try:
            engine = await self._obtener_engine()
            async with engine.connect() as conn:
                result = await conn.execute(sql)
                columnas = result.keys()
                filas = []
                for row in result.fetchall():
                    fila = {}
                    for i, columna in enumerate(columnas):
                        valor = row[i]
                        if isinstance(valor, (datetime, date)):
                            valor = valor.isoformat()
                        elif isinstance(valor, Decimal):
                            valor = float(valor)
                        elif isinstance(valor, UUID):
                            valor = str(valor)
                        fila[columna] = valor
                    filas.append(fila)
                return filas
        except Exception as ex:
            raise RuntimeError(
                f"Error SQL Server al consultar '{esquema_final}.{nombre_tabla}': {ex}"
            ) from ex

    async def obtener_por_clave(
        self, nombre_tabla: str, nombre_clave: str, valor: str, esquema: str | None = None
    ) -> list[dict[str, Any]]:
        """Obtiene filas filtradas por una columna y valor."""
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío")
        if not nombre_clave or not nombre_clave.strip():
            raise ValueError("El nombre de la clave no puede estar vacío")
        if not valor or not valor.strip():
            raise ValueError("El valor no puede estar vacío")

        esquema_final = (esquema or "dbo").strip()

        try:
            tipo_columna = await self._detectar_tipo_columna(
                nombre_tabla, esquema_final, nombre_clave
            )

            # Si buscan una fecha en una columna DATETIME, comparar solo la parte DATE
            if (tipo_columna in ('datetime', 'datetime2')
                    and self._es_fecha_sin_hora(valor)):
                sql = text(f"""
                    SELECT * FROM [{esquema_final}].[{nombre_tabla}]
                    WHERE CAST([{nombre_clave}] AS DATE) = :valor
                """)
                valor_convertido = self._extraer_solo_fecha(valor)
            else:
                sql = text(f"""
                    SELECT * FROM [{esquema_final}].[{nombre_tabla}]
                    WHERE [{nombre_clave}] = :valor
                """)
                valor_convertido = self._convertir_valor(valor, tipo_columna)

            engine = await self._obtener_engine()
            async with engine.connect() as conn:
                result = await conn.execute(sql, {"valor": valor_convertido})
                columnas = result.keys()
                filas = []
                for row in result.fetchall():
                    fila = {}
                    for i, columna in enumerate(columnas):
                        val = row[i]
                        if isinstance(val, (datetime, date)):
                            val = val.isoformat()
                        elif isinstance(val, Decimal):
                            val = float(val)
                        elif isinstance(val, UUID):
                            val = str(val)
                        fila[columna] = val
                    filas.append(fila)
                return filas
        except Exception as ex:
            raise RuntimeError(
                f"Error SQL Server al filtrar '{esquema_final}.{nombre_tabla}': {ex}"
            ) from ex

    async def crear(
        self, nombre_tabla: str, datos: dict[str, Any],
        esquema: str | None = None, campos_encriptar: str | None = None
    ) -> bool:
        """Inserta una nueva fila en la tabla."""
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío")
        if not datos:
            raise ValueError("Los datos no pueden estar vacíos")

        esquema_final = (esquema or "dbo").strip()
        datos_finales = dict(datos)

        if campos_encriptar:
            campos_a_encriptar = {
                c.strip().lower() for c in campos_encriptar.split(',') if c.strip()
            }
            for campo in list(datos_finales.keys()):
                if campo.lower() in campos_a_encriptar and datos_finales[campo]:
                    datos_finales[campo] = encriptar(str(datos_finales[campo]))

        columnas = ", ".join(f"[{k}]" for k in datos_finales.keys())
        parametros = ", ".join(f":{k}" for k in datos_finales.keys())
        sql = text(f"INSERT INTO [{esquema_final}].[{nombre_tabla}] ({columnas}) VALUES ({parametros})")

        try:
            valores = {}
            for key, val in datos_finales.items():
                if val is not None and isinstance(val, str):
                    tipo = await self._detectar_tipo_columna(nombre_tabla, esquema_final, key)
                    valores[key] = self._convertir_valor(val, tipo)
                else:
                    valores[key] = val

            engine = await self._obtener_engine()
            async with engine.begin() as conn:
                result = await conn.execute(sql, valores)
                return result.rowcount > 0
        except Exception as ex:
            raise RuntimeError(
                f"Error SQL Server al insertar en '{esquema_final}.{nombre_tabla}': {ex}"
            ) from ex

    async def actualizar(
        self, nombre_tabla: str, nombre_clave: str, valor_clave: str,
        datos: dict[str, Any], esquema: str | None = None, campos_encriptar: str | None = None
    ) -> int:
        """Actualiza filas que coincidan con la clave. Retorna filas afectadas."""
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío")
        if not nombre_clave or not nombre_clave.strip():
            raise ValueError("El nombre de la clave no puede estar vacío")
        if not valor_clave or not valor_clave.strip():
            raise ValueError("El valor de la clave no puede estar vacío")
        if not datos:
            raise ValueError("Los datos no pueden estar vacíos")

        esquema_final = (esquema or "dbo").strip()
        datos_finales = dict(datos)

        if campos_encriptar:
            campos_a_encriptar = {
                c.strip().lower() for c in campos_encriptar.split(',') if c.strip()
            }
            for campo in list(datos_finales.keys()):
                if campo.lower() in campos_a_encriptar and datos_finales[campo]:
                    datos_finales[campo] = encriptar(str(datos_finales[campo]))

        clausula_set = ", ".join(f"[{k}] = :{k}" for k in datos_finales.keys())
        sql = text(f"""
            UPDATE [{esquema_final}].[{nombre_tabla}]
            SET {clausula_set}
            WHERE [{nombre_clave}] = :valor_clave
        """)

        try:
            valores = {}
            for key, val in datos_finales.items():
                if val is not None and isinstance(val, str):
                    tipo = await self._detectar_tipo_columna(nombre_tabla, esquema_final, key)
                    valores[key] = self._convertir_valor(val, tipo)
                else:
                    valores[key] = val

            tipo_clave = await self._detectar_tipo_columna(
                nombre_tabla, esquema_final, nombre_clave
            )
            valores["valor_clave"] = self._convertir_valor(valor_clave, tipo_clave)

            engine = await self._obtener_engine()
            async with engine.begin() as conn:
                result = await conn.execute(sql, valores)
                return result.rowcount
        except Exception as ex:
            raise RuntimeError(
                f"Error SQL Server al actualizar '{esquema_final}.{nombre_tabla}': {ex}"
            ) from ex

    async def eliminar(
        self, nombre_tabla: str, nombre_clave: str, valor_clave: str,
        esquema: str | None = None
    ) -> int:
        """Elimina filas que coincidan con la clave. Retorna filas eliminadas."""
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío")
        if not nombre_clave or not nombre_clave.strip():
            raise ValueError("El nombre de la clave no puede estar vacío")
        if not valor_clave or not valor_clave.strip():
            raise ValueError("El valor de la clave no puede estar vacío")

        esquema_final = (esquema or "dbo").strip()

        sql = text(f"""
            DELETE FROM [{esquema_final}].[{nombre_tabla}]
            WHERE [{nombre_clave}] = :valor_clave
        """)

        try:
            tipo_clave = await self._detectar_tipo_columna(
                nombre_tabla, esquema_final, nombre_clave
            )
            valor_convertido = self._convertir_valor(valor_clave, tipo_clave)

            engine = await self._obtener_engine()
            async with engine.begin() as conn:
                result = await conn.execute(sql, {"valor_clave": valor_convertido})
                return result.rowcount
        except Exception as ex:
            raise RuntimeError(
                f"Error SQL Server al eliminar de '{esquema_final}.{nombre_tabla}': {ex}"
            ) from ex

    async def obtener_hash_contrasena(
        self, nombre_tabla: str, campo_usuario: str, campo_contrasena: str,
        valor_usuario: str, esquema: str | None = None
    ) -> str | None:
        """Obtiene el hash BCrypt almacenado para un usuario."""
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío")
        if not campo_usuario or not campo_usuario.strip():
            raise ValueError("El campo de usuario no puede estar vacío")
        if not campo_contrasena or not campo_contrasena.strip():
            raise ValueError("El campo de contraseña no puede estar vacío")
        if not valor_usuario or not valor_usuario.strip():
            raise ValueError("El valor de usuario no puede estar vacío")

        esquema_final = (esquema or "dbo").strip()

        sql = text(f"""
            SELECT [{campo_contrasena}]
            FROM [{esquema_final}].[{nombre_tabla}]
            WHERE [{campo_usuario}] = :valor_usuario
        """)

        try:
            engine = await self._obtener_engine()
            async with engine.connect() as conn:
                result = await conn.execute(sql, {"valor_usuario": valor_usuario})
                row = result.fetchone()
                return str(row[0]) if row and row[0] else None
        except Exception as ex:
            raise RuntimeError(
                f"Error SQL Server al obtener hash de '{esquema_final}.{nombre_tabla}': {ex}"
            ) from ex
