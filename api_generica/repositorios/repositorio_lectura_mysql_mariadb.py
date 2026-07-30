"""
repositorio_lectura_mysql_mariadb.py — Repositorio CRUD para MySQL y MariaDB.

Características de MySQL/MariaDB:
- Identificadores con `backticks`
- LIMIT n para limitar resultados
- No usa esquemas tradicionales (la base de datos es el contenedor)
- Soporta cadenas de conexión en formato C# (Server=...;Port=...;...)
"""

from typing import Any
from datetime import datetime, date, time, timedelta
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from servicios.abstracciones.i_proveedor_conexion import IProveedorConexion
from servicios.utilidades.encriptacion_bcrypt import encriptar


class RepositorioLecturaMysqlMariaDB:
    """Implementación de acceso a datos para MySQL y MariaDB usando SQLAlchemy async."""

    def __init__(self, proveedor_conexion: IProveedorConexion):
        if proveedor_conexion is None:
            raise ValueError("proveedor_conexion no puede ser None")
        self._proveedor_conexion = proveedor_conexion
        self._engine: AsyncEngine | None = None

    def _convertir_cadena_csharp_a_sqlalchemy(self, cadena: str) -> str:
        """
        Convierte una cadena en formato C# (Server=...;Port=...;...) a URL de SQLAlchemy.
        Si ya es formato URL (mysql+...), la retorna tal cual.
        """
        if cadena.startswith("mysql+") or cadena.startswith("mariadb+"):
            return cadena

        # Parsear formato key=value;key=value;...
        partes = {}
        for segmento in cadena.split(";"):
            segmento = segmento.strip()
            if "=" in segmento:
                clave, valor = segmento.split("=", 1)
                partes[clave.strip().lower()] = valor.strip()

        host = partes.get("server", "localhost")
        port = partes.get("port", "3306")
        database = partes.get("database", "")
        user = partes.get("user", partes.get("uid", "root"))
        password = partes.get("password", partes.get("pwd", ""))

        if password:
            return f"mysql+aiomysql://{user}:{password}@{host}:{port}/{database}"
        return f"mysql+aiomysql://{user}@{host}:{port}/{database}"

    async def _obtener_engine(self) -> AsyncEngine:
        """Crea el engine de conexión la primera vez, luego lo reutiliza."""
        if self._engine is None:
            cadena = self._proveedor_conexion.obtener_cadena_conexion()
            cadena_sqlalchemy = self._convertir_cadena_csharp_a_sqlalchemy(cadena)
            self._engine = create_async_engine(cadena_sqlalchemy, echo=False)
        return self._engine

    # --- Métodos auxiliares para detectar y convertir tipos ---

    async def _detectar_tipo_columna(
        self, nombre_tabla: str, nombre_columna: str
    ) -> str | None:
        """Consulta information_schema para saber el tipo de una columna."""
        sql = text("""
            SELECT DATA_TYPE
            FROM information_schema.columns
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = :tabla
            AND COLUMN_NAME = :columna
        """)
        try:
            engine = await self._obtener_engine()
            async with engine.connect() as conn:
                result = await conn.execute(sql, {
                    "tabla": nombre_tabla, "columna": nombre_columna
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
            if tipo_destino in ('int', 'integer', 'bigint', 'smallint', 'tinyint', 'mediumint'):
                return int(valor)
            if tipo_destino in ('decimal', 'numeric'):
                return Decimal(valor)
            if tipo_destino in ('float', 'double', 'real'):
                return float(valor)
            if tipo_destino == 'bit':
                return valor.lower() in ('true', '1', 'yes', 'si')
            if tipo_destino == 'date':
                return self._extraer_solo_fecha(valor)
            if tipo_destino in ('datetime', 'timestamp'):
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

    def _serializar_valor(self, valor: Any) -> Any:
        """Convierte tipos Python a tipos que FastAPI puede serializar a JSON."""
        if isinstance(valor, (datetime, date)):
            return valor.isoformat()
        elif isinstance(valor, time):
            return valor.isoformat()
        elif isinstance(valor, timedelta):
            return str(valor)
        elif isinstance(valor, Decimal):
            return float(valor)
        elif isinstance(valor, bytes):
            return valor.decode('utf-8', errors='replace')
        return valor

    # --- Operaciones CRUD ---

    async def obtener_filas(
        self, nombre_tabla: str, esquema: str | None = None, limite: int | None = None
    ) -> list[dict[str, Any]]:
        """Obtiene filas de una tabla con LIMIT opcional."""
        if not nombre_tabla or not nombre_tabla.strip():
            raise ValueError("El nombre de la tabla no puede estar vacío")

        limite_final = limite or 1000
        prefijo_esquema = f"`{esquema}`." if esquema else ""

        sql = text(f"SELECT * FROM {prefijo_esquema}`{nombre_tabla}` LIMIT :limite")

        try:
            engine = await self._obtener_engine()
            async with engine.connect() as conn:
                result = await conn.execute(sql, {"limite": limite_final})
                columnas = result.keys()
                return [
                    {col: self._serializar_valor(row[i]) for i, col in enumerate(columnas)}
                    for row in result.fetchall()
                ]
        except Exception as ex:
            raise RuntimeError(
                f"Error MySQL/MariaDB al consultar '{nombre_tabla}': {ex}"
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

        prefijo_esquema = f"`{esquema}`." if esquema else ""

        try:
            tipo_columna = await self._detectar_tipo_columna(nombre_tabla, nombre_clave)

            if (tipo_columna in ('datetime', 'timestamp')
                    and self._es_fecha_sin_hora(valor)):
                sql = text(f'''
                    SELECT * FROM {prefijo_esquema}`{nombre_tabla}`
                    WHERE DATE(`{nombre_clave}`) = :valor
                ''')
                valor_convertido = self._extraer_solo_fecha(valor)
            else:
                sql = text(f'''
                    SELECT * FROM {prefijo_esquema}`{nombre_tabla}`
                    WHERE `{nombre_clave}` = :valor
                ''')
                valor_convertido = self._convertir_valor(valor, tipo_columna)

            engine = await self._obtener_engine()
            async with engine.connect() as conn:
                result = await conn.execute(sql, {"valor": valor_convertido})
                columnas = result.keys()
                return [
                    {col: self._serializar_valor(row[i]) for i, col in enumerate(columnas)}
                    for row in result.fetchall()
                ]
        except Exception as ex:
            raise RuntimeError(
                f"Error MySQL/MariaDB al filtrar '{nombre_tabla}': {ex}"
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

        prefijo_esquema = f"`{esquema}`." if esquema else ""
        datos_finales = dict(datos)

        if campos_encriptar:
            campos_a_encriptar = {
                c.strip().lower() for c in campos_encriptar.split(',') if c.strip()
            }
            for campo in list(datos_finales.keys()):
                if campo.lower() in campos_a_encriptar and datos_finales[campo]:
                    datos_finales[campo] = encriptar(str(datos_finales[campo]))

        columnas = ", ".join(f"`{k}`" for k in datos_finales.keys())
        parametros = ", ".join(f":p_{k}" for k in datos_finales.keys())
        sql = text(f"INSERT INTO {prefijo_esquema}`{nombre_tabla}` ({columnas}) VALUES ({parametros})")

        try:
            valores = {}
            for key, val in datos_finales.items():
                if val is not None and isinstance(val, str):
                    tipo = await self._detectar_tipo_columna(nombre_tabla, key)
                    valores[f"p_{key}"] = self._convertir_valor(val, tipo)
                else:
                    valores[f"p_{key}"] = val

            engine = await self._obtener_engine()
            async with engine.begin() as conn:
                result = await conn.execute(sql, valores)
                return result.rowcount > 0
        except Exception as ex:
            raise RuntimeError(
                f"Error MySQL/MariaDB al insertar en '{nombre_tabla}': {ex}"
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

        prefijo_esquema = f"`{esquema}`." if esquema else ""
        datos_finales = dict(datos)

        if campos_encriptar:
            campos_a_encriptar = {
                c.strip().lower() for c in campos_encriptar.split(',') if c.strip()
            }
            for campo in list(datos_finales.keys()):
                if campo.lower() in campos_a_encriptar and datos_finales[campo]:
                    datos_finales[campo] = encriptar(str(datos_finales[campo]))

        clausula_set = ", ".join(f"`{k}` = :p_{k}" for k in datos_finales.keys())
        sql = text(f'''
            UPDATE {prefijo_esquema}`{nombre_tabla}`
            SET {clausula_set}
            WHERE `{nombre_clave}` = :valor_clave
        ''')

        try:
            valores = {}
            for key, val in datos_finales.items():
                if val is not None and isinstance(val, str):
                    tipo = await self._detectar_tipo_columna(nombre_tabla, key)
                    valores[f"p_{key}"] = self._convertir_valor(val, tipo)
                else:
                    valores[f"p_{key}"] = val

            valores["valor_clave"] = valor_clave

            engine = await self._obtener_engine()
            async with engine.begin() as conn:
                result = await conn.execute(sql, valores)
                return result.rowcount
        except Exception as ex:
            raise RuntimeError(
                f"Error MySQL/MariaDB al actualizar '{nombre_tabla}': {ex}"
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

        prefijo_esquema = f"`{esquema}`." if esquema else ""

        sql = text(f'''
            DELETE FROM {prefijo_esquema}`{nombre_tabla}`
            WHERE `{nombre_clave}` = :valor_clave
        ''')

        try:
            engine = await self._obtener_engine()
            async with engine.begin() as conn:
                result = await conn.execute(sql, {"valor_clave": valor_clave})
                return result.rowcount
        except Exception as ex:
            raise RuntimeError(
                f"Error MySQL/MariaDB al eliminar de '{nombre_tabla}': {ex}"
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

        prefijo_esquema = f"`{esquema}`." if esquema else ""

        sql = text(f'''
            SELECT `{campo_contrasena}`
            FROM {prefijo_esquema}`{nombre_tabla}`
            WHERE `{campo_usuario}` = :valor_usuario
            LIMIT 1
        ''')

        try:
            engine = await self._obtener_engine()
            async with engine.connect() as conn:
                result = await conn.execute(sql, {"valor_usuario": valor_usuario})
                row = result.fetchone()
                return str(row[0]) if row and row[0] else None
        except Exception as ex:
            raise RuntimeError(
                f"Error MySQL/MariaDB al obtener hash de '{nombre_tabla}': {ex}"
            ) from ex
