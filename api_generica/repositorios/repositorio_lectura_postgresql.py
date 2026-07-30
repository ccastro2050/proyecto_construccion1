"""
repositorio_lectura_postgresql.py — Repositorio CRUD para PostgreSQL.

Características de PostgreSQL:
- Identificadores con "comillas dobles"
- LIMIT n para limitar resultados
- Esquema por defecto: 'public'
"""

from typing import Any
from datetime import datetime, date, time
from decimal import Decimal
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from servicios.abstracciones.i_proveedor_conexion import IProveedorConexion
from servicios.utilidades.encriptacion_bcrypt import encriptar


class RepositorioLecturaPostgreSQL:
    """Implementación de acceso a datos para PostgreSQL usando SQLAlchemy async."""

    def __init__(self, proveedor_conexion: IProveedorConexion):
        if proveedor_conexion is None:
            raise ValueError("proveedor_conexion no puede ser None")
        self._proveedor_conexion = proveedor_conexion
        self._engine: AsyncEngine | None = None

    async def _obtener_engine(self) -> AsyncEngine:
        """Crea el engine de conexión la primera vez, luego lo reutiliza."""
        if self._engine is None:
            cadena = self._proveedor_conexion.obtener_cadena_conexion()
            self._engine = create_async_engine(cadena, echo=False)
        return self._engine

    # --- Métodos auxiliares para detectar y convertir tipos ---

    async def _detectar_tipo_columna(
        self, nombre_tabla: str, esquema: str, nombre_columna: str
    ) -> str | None:
        """Consulta information_schema para saber el tipo de una columna."""
        sql = text("""
            SELECT data_type, udt_name
            FROM information_schema.columns
            WHERE table_schema = :esquema
            AND table_name = :tabla
            AND column_name = :columna
        """)
        try:
            engine = await self._obtener_engine()
            async with engine.connect() as conn:
                result = await conn.execute(sql, {
                    "esquema": esquema, "tabla": nombre_tabla,
                    "columna": nombre_columna
                })
                row = result.fetchone()
                return row[0].lower() if row else None
        except Exception:
            return None

    def _convertir_valor(self, valor: str, tipo_destino: str | None) -> Any:
        """Convierte un string al tipo Python que corresponde."""
        if tipo_destino is None:
            return valor
        try:
            if tipo_destino in ('integer', 'int4', 'bigint', 'int8',
                                'smallint', 'int2'):
                return int(valor)
            if tipo_destino in ('numeric', 'decimal'):
                return Decimal(valor)
            if tipo_destino in ('real', 'float4', 'double precision', 'float8'):
                return float(valor)
            if tipo_destino in ('boolean', 'bool'):
                return valor.lower() in ('true', '1', 'yes', 'si', 't')
            if tipo_destino == 'uuid':
                return UUID(valor)
            if tipo_destino == 'date':
                return self._extraer_solo_fecha(valor)
            if tipo_destino in ('timestamp without time zone',
                                'timestamp with time zone'):
                return datetime.fromisoformat(valor.replace('Z', '+00:00'))
            if tipo_destino == 'time':
                return time.fromisoformat(valor)
            return valor
        except (ValueError, TypeError):
            return valor

    def _extraer_solo_fecha(self, valor: str) -> date:
        """Extrae la parte de fecha de un string ISO."""
        if 'T' in valor:
            return datetime.fromisoformat(
                valor.replace('Z', '+00:00')
            ).date()
        return date.fromisoformat(valor[:10])

    def _es_fecha_sin_hora(self, valor: str) -> bool:
        """Detecta si un valor tiene formato YYYY-MM-DD (solo fecha)."""
        return (len(valor) == 10 and valor.count('-') == 2
                and 'T' not in valor)

    def _serializar_valor(self, valor: Any) -> Any:
        """Convierte tipos Python a tipos serializables para JSON."""
        if isinstance(valor, (datetime, date)):
            return valor.isoformat()
        elif isinstance(valor, Decimal):
            return float(valor)
        elif isinstance(valor, UUID):
            return str(valor)
        return valor

    # --- Operaciones CRUD ---

    async def obtener_filas(
        self, nombre_tabla: str, esquema: str | None = None,
        limite: int | None = None
    ) -> list[dict[str, Any]]:
        """Obtiene filas de una tabla con LIMIT opcional."""
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío")

        esquema_final = (esquema or "public").strip()
        limite_final = limite or 1000

        sql = text(
            f'SELECT * FROM "{esquema_final}"."{nombre_tabla}" LIMIT :limite'
        )

        try:
            engine = await self._obtener_engine()
            async with engine.connect() as conn:
                result = await conn.execute(sql, {"limite": limite_final})
                columnas = result.keys()
                return [
                    {col: self._serializar_valor(row[i])
                     for i, col in enumerate(columnas)}
                    for row in result.fetchall()
                ]
        except Exception as ex:
            raise RuntimeError(
                f"Error PostgreSQL al consultar "
                f"'{esquema_final}.{nombre_tabla}': {ex}"
            ) from ex

    async def obtener_por_clave(
        self, nombre_tabla: str, nombre_clave: str, valor: str,
        esquema: str | None = None
    ) -> list[dict[str, Any]]:
        """Obtiene filas filtradas por una columna y valor."""
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío")
        if not nombre_clave or not nombre_clave.strip():
            raise ValueError("El nombre de la clave no puede estar vacío")
        if not valor or not valor.strip():
            raise ValueError("El valor no puede estar vacío")

        esquema_final = (esquema or "public").strip()

        try:
            tipo_columna = await self._detectar_tipo_columna(
                nombre_tabla, esquema_final, nombre_clave
            )

            # Si buscan una fecha en una columna TIMESTAMP,
            # comparar solo la parte DATE
            if (tipo_columna in ('timestamp without time zone',
                                 'timestamp with time zone')
                    and self._es_fecha_sin_hora(valor)):
                sql = text(f'''
                    SELECT * FROM "{esquema_final}"."{nombre_tabla}"
                    WHERE CAST("{nombre_clave}" AS DATE) = :valor
                ''')
                valor_convertido = self._extraer_solo_fecha(valor)
            else:
                sql = text(f'''
                    SELECT * FROM "{esquema_final}"."{nombre_tabla}"
                    WHERE "{nombre_clave}" = :valor
                ''')
                valor_convertido = self._convertir_valor(
                    valor, tipo_columna
                )

            engine = await self._obtener_engine()
            async with engine.connect() as conn:
                result = await conn.execute(
                    sql, {"valor": valor_convertido}
                )
                columnas = result.keys()
                return [
                    {col: self._serializar_valor(row[i])
                     for i, col in enumerate(columnas)}
                    for row in result.fetchall()
                ]
        except Exception as ex:
            raise RuntimeError(
                f"Error PostgreSQL al filtrar "
                f"'{esquema_final}.{nombre_tabla}': {ex}"
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

        esquema_final = (esquema or "public").strip()
        datos_finales = dict(datos)

        # Encriptar campos indicados (ej: contraseñas)
        if campos_encriptar:
            campos_a_encriptar = {
                c.strip().lower()
                for c in campos_encriptar.split(',') if c.strip()
            }
            for campo in list(datos_finales.keys()):
                if (campo.lower() in campos_a_encriptar
                        and datos_finales[campo]):
                    datos_finales[campo] = encriptar(
                        str(datos_finales[campo])
                    )

        columnas = ", ".join(f'"{k}"' for k in datos_finales.keys())
        parametros = ", ".join(f":{k}" for k in datos_finales.keys())
        sql = text(
            f'INSERT INTO "{esquema_final}"."{nombre_tabla}" '
            f'({columnas}) VALUES ({parametros})'
        )

        try:
            valores = {}
            for key, val in datos_finales.items():
                if val is not None and isinstance(val, str):
                    tipo = await self._detectar_tipo_columna(
                        nombre_tabla, esquema_final, key
                    )
                    valores[key] = self._convertir_valor(val, tipo)
                else:
                    valores[key] = val

            engine = await self._obtener_engine()
            async with engine.begin() as conn:
                result = await conn.execute(sql, valores)
                return result.rowcount > 0
        except Exception as ex:
            raise RuntimeError(
                f"Error PostgreSQL al insertar en "
                f"'{esquema_final}.{nombre_tabla}': {ex}"
            ) from ex

    async def actualizar(
        self, nombre_tabla: str, nombre_clave: str, valor_clave: str,
        datos: dict[str, Any], esquema: str | None = None,
        campos_encriptar: str | None = None
    ) -> int:
        """Actualiza filas. Retorna filas afectadas."""
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío")
        if not nombre_clave or not nombre_clave.strip():
            raise ValueError("El nombre de la clave no puede estar vacío")
        if not valor_clave or not valor_clave.strip():
            raise ValueError("El valor de la clave no puede estar vacío")
        if not datos:
            raise ValueError("Los datos no pueden estar vacíos")

        esquema_final = (esquema or "public").strip()
        datos_finales = dict(datos)

        if campos_encriptar:
            campos_a_encriptar = {
                c.strip().lower()
                for c in campos_encriptar.split(',') if c.strip()
            }
            for campo in list(datos_finales.keys()):
                if (campo.lower() in campos_a_encriptar
                        and datos_finales[campo]):
                    datos_finales[campo] = encriptar(
                        str(datos_finales[campo])
                    )

        clausula_set = ", ".join(
            f'"{k}" = :{k}' for k in datos_finales.keys()
        )
        sql = text(f'''
            UPDATE "{esquema_final}"."{nombre_tabla}"
            SET {clausula_set}
            WHERE "{nombre_clave}" = :valor_clave
        ''')

        try:
            valores = {}
            for key, val in datos_finales.items():
                if val is not None and isinstance(val, str):
                    tipo = await self._detectar_tipo_columna(
                        nombre_tabla, esquema_final, key
                    )
                    valores[key] = self._convertir_valor(val, tipo)
                else:
                    valores[key] = val

            tipo_clave = await self._detectar_tipo_columna(
                nombre_tabla, esquema_final, nombre_clave
            )
            valores["valor_clave"] = self._convertir_valor(
                valor_clave, tipo_clave
            )

            engine = await self._obtener_engine()
            async with engine.begin() as conn:
                result = await conn.execute(sql, valores)
                return result.rowcount
        except Exception as ex:
            raise RuntimeError(
                f"Error PostgreSQL al actualizar "
                f"'{esquema_final}.{nombre_tabla}': {ex}"
            ) from ex

    async def eliminar(
        self, nombre_tabla: str, nombre_clave: str, valor_clave: str,
        esquema: str | None = None
    ) -> int:
        """Elimina filas. Retorna filas eliminadas."""
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío")
        if not nombre_clave or not nombre_clave.strip():
            raise ValueError("El nombre de la clave no puede estar vacío")
        if not valor_clave or not valor_clave.strip():
            raise ValueError("El valor de la clave no puede estar vacío")

        esquema_final = (esquema or "public").strip()

        sql = text(f'''
            DELETE FROM "{esquema_final}"."{nombre_tabla}"
            WHERE "{nombre_clave}" = :valor_clave
        ''')

        try:
            tipo_clave = await self._detectar_tipo_columna(
                nombre_tabla, esquema_final, nombre_clave
            )
            valor_convertido = self._convertir_valor(
                valor_clave, tipo_clave
            )

            engine = await self._obtener_engine()
            async with engine.begin() as conn:
                result = await conn.execute(
                    sql, {"valor_clave": valor_convertido}
                )
                return result.rowcount
        except Exception as ex:
            raise RuntimeError(
                f"Error PostgreSQL al eliminar de "
                f"'{esquema_final}.{nombre_tabla}': {ex}"
            ) from ex

    async def obtener_hash_contrasena(
        self, nombre_tabla: str, campo_usuario: str,
        campo_contrasena: str, valor_usuario: str,
        esquema: str | None = None
    ) -> str | None:
        """Obtiene el hash BCrypt almacenado para un usuario."""
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío")
        if not campo_usuario or not campo_usuario.strip():
            raise ValueError("El campo de usuario no puede estar vacío")
        if not campo_contrasena or not campo_contrasena.strip():
            raise ValueError(
                "El campo de contraseña no puede estar vacío"
            )
        if not valor_usuario or not valor_usuario.strip():
            raise ValueError("El valor de usuario no puede estar vacío")

        esquema_final = (esquema or "public").strip()

        sql = text(f'''
            SELECT "{campo_contrasena}"
            FROM "{esquema_final}"."{nombre_tabla}"
            WHERE "{campo_usuario}" = :valor_usuario
        ''')

        try:
            engine = await self._obtener_engine()
            async with engine.connect() as conn:
                result = await conn.execute(
                    sql, {"valor_usuario": valor_usuario}
                )
                row = result.fetchone()
                return str(row[0]) if row and row[0] else None
        except Exception as ex:
            raise RuntimeError(
                f"Error PostgreSQL al obtener hash de "
                f"'{esquema_final}.{nombre_tabla}': {ex}"
            ) from ex
