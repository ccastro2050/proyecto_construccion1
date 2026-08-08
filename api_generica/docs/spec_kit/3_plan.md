# Plan técnico — API Genérica CRUD

> **Documento 3 de 8** del spec kit: **CÓMO** construir lo especificado en
> [2_spec.md](2_spec.md). El porqué de cada decisión: [4_research.md](4_research.md) ·
> endpoints exactos: [6_contracts.md](6_contracts.md) · orden de trabajo: [8_tasks.md](8_tasks.md).

---

## 1. Stack

| Pieza | Elección | Por qué |
|---|---|---|
| Lenguaje | Python 3.12 | Imagen base `python:3.12-slim` |
| Framework web | FastAPI ≥ 0.100 | Async nativo, Swagger automático, validación de tipos |
| Servidor | uvicorn ≥ 0.22 | Servidor ASGI estándar para FastAPI |
| Acceso a datos | SQLAlchemy 2 async (`sqlalchemy[asyncio]` + `greenlet`) | Un solo estilo de query (`text()` + parámetros) para los 3 motores |
| Driver PostgreSQL | asyncpg | Async puro |
| Driver MySQL/MariaDB | aiomysql (+ `cryptography` para auth sha256) | Async puro |
| Driver SQL Server | aioodbc + **msodbcsql18** (paquete del SO) | SQL Server solo habla ODBC; el driver se instala con `apt-get` en el Dockerfile, no con pip |
| Configuración | pydantic-settings + python-dotenv | Lee `.env` y variables de entorno con prefijo `DB_` |
| Contraseñas | bcrypt (y passlib) | Hash de 60 caracteres, costo 12 |

## 2. Estructura de carpetas

```
api_generica/
├── Dockerfile                  # python:3.12-slim + msodbcsql18 + pip install
├── requirements.txt
├── config.py                   # Settings con pydantic-settings (singleton @lru_cache)
├── main.py                     # crea FastAPI, CORS, registra router, endpoint /
├── controllers/
│   └── entidades_controller.py # los 6 endpoints HTTP (router prefix="/api")
├── servicios/
│   ├── abstracciones/
│   │   ├── i_proveedor_conexion.py   # Protocol: proveedor_actual, obtener_cadena_conexion()
│   │   └── i_servicio_crud.py        # Protocol del servicio
│   ├── conexion/
│   │   └── proveedor_conexion.py     # lee DB_PROVIDER y entrega la cadena del motor activo
│   ├── utilidades/
│   │   └── encriptacion_bcrypt.py    # encriptar(valor, costo=12) / verificar(valor, hash)
│   ├── servicio_crud.py              # lógica de negocio (validaciones, normalización)
│   └── fabrica_repositorios.py       # Factory: DB_PROVIDER → clase de repositorio
└── repositorios/
    ├── abstracciones/
    │   └── i_repositorio_lectura_tabla.py  # Protocol con los 6 métodos de datos
    ├── repositorio_lectura_postgresql.py
    ├── repositorio_lectura_mysql_mariadb.py
    └── repositorio_lectura_sqlserver.py
```

## 3. Arquitectura en capas (flujo de una petición)

```
HTTP → entidades_controller (valida entrada, traduce excepciones a códigos HTTP)
     → fabrica_repositorios.crear_servicio_crud()
     → ServicioCrud (valida reglas: nombres no vacíos, normaliza esquema/límite)
     → RepositorioLectura<Motor> (arma y ejecuta el SQL específico del motor)
     → SQLAlchemy async engine → base de datos
```

**Regla de dependencias:** el controller solo conoce al servicio; el servicio solo
conoce la **interfaz** `IRepositorioLecturaTabla` (inversión de dependencias, la D
de SOLID); solo la fábrica conoce las clases concretas de repositorio.

## 4. Decisiones de diseño clave

### 4.1 Interfaces con `typing.Protocol`
Los contratos (`i_repositorio_lectura_tabla`, `i_proveedor_conexion`, `i_servicio_crud`)
se definen como `Protocol`: cualquier clase con esos métodos cumple el contrato sin
heredar (duck typing verificable). Prefijo `i_` en archivo, `I` en clase.

### 4.2 Patrón Factory con diccionario
`fabrica_repositorios.py` mapea nombre de proveedor → clase:

```python
_REPOSITORIOS_LECTURA = {
    "sqlserver": RepositorioLecturaSqlServer,
    "sqlserverexpress": RepositorioLecturaSqlServer,
    "localdb": RepositorioLecturaSqlServer,
    "postgres": RepositorioLecturaPostgreSQL,
    "postgresql": RepositorioLecturaPostgreSQL,
    "mysql": RepositorioLecturaMysqlMariaDB,
    "mariadb": RepositorioLecturaMysqlMariaDB,
}
```
Agregar un motor nuevo = escribir su repositorio + 1 línea aquí (principio
abierto/cerrado, la O de SOLID). El controller crea servicio y repositorio **por
petición** llamando `crear_servicio_crud()`.

### 4.3 Configuración con pydantic-settings
- `DatabaseSettings` con `env_prefix='DB_'`: lee `DB_PROVIDER`, `DB_POSTGRES`,
  `DB_MARIADB`, `DB_MYSQL`, `DB_SQLSERVER`, `DB_SQLSERVEREXPRESS`, `DB_LOCALDB`.
- `Settings` agrupa `debug`, `environment` y `database`.
- `get_settings()` con `@lru_cache()` = singleton.
- En desarrollo (`ENVIRONMENT=development`) carga `.env` + `.env.development`.
- En Docker las variables llegan por `environment:` del compose (no hace falta `.env`).

Cadenas de conexión (formato SQLAlchemy async):
```
postgresql+asyncpg://usuario:clave@host:5432/base
mysql+aiomysql://usuario:clave@host:3306/base
mssql+aioodbc://usuario:clave@host:1433/base?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```

### 4.4 SQL genérico: mismo algoritmo, dialecto distinto
Los 3 repositorios implementan los mismos 6 métodos; solo cambia el dialecto:

| Aspecto | PostgreSQL | MySQL/MariaDB | SQL Server |
|---|---|---|---|
| Comillas de identificador | `"tabla"` | `` `tabla` `` | `[tabla]` |
| Limitar filas | `LIMIT :n` | `LIMIT :n` | `SELECT TOP (n)` |
| Esquema por defecto | `public` | la BD misma (no antepone esquema) | `dbo` |
| Catálogo de tipos | `information_schema.columns` | `information_schema.columns` | `information_schema.columns` |

Métodos de cada repositorio: `obtener_filas`, `obtener_por_clave`, `crear`,
`actualizar`, `eliminar`, `obtener_hash_contrasena`.

Helpers privados comunes a los 3 (se repiten adaptados por motor):
- `_obtener_engine()` — crea el `AsyncEngine` una sola vez y lo reutiliza (lazy).
- `_detectar_tipo_columna(tabla, esquema, columna)` — consulta `information_schema`.
- `_convertir_valor(valor_str, tipo)` — string de la URL → `int`, `Decimal`, `float`,
  `bool`, `UUID`, `date`, `datetime`, `time` según el tipo real de la columna.
- `_serializar_valor(valor)` — `datetime/date` → ISO, `Decimal` → float, `UUID` → str.
- `_es_fecha_sin_hora(valor)` / `_extraer_solo_fecha(valor)` — para el caso especial
  de filtrar TIMESTAMP por fecha (`CAST(col AS DATE)`).

**Siempre parámetros nombrados** (`:valor`), nunca concatenar valores en el SQL
(previene inyección SQL en los VALORES; los nombres de tabla/columna van entre
comillas del dialecto).

### 4.5 Encriptación BCrypt
`encriptacion_bcrypt.py` expone dos funciones puras:
- `encriptar(valor, costo=12) -> str` — `bcrypt.gensalt(rounds=costo)` + `hashpw`.
- `verificar(valor, hash) -> bool` — `bcrypt.checkpw`, devuelve `False` ante cualquier error.

El **repositorio** encripta al crear/actualizar si llega `campos_encriptar`
(nombres separados por coma, comparación case-insensitive). El **servicio** usa
`verificar()` para `verificar_contrasena` y devuelve tuplas `(código, mensaje)`:
`(200, "Contraseña válida.")`, `(404, "Usuario no encontrado.")`, `(401, "Contraseña incorrecta.")`.

### 4.6 Traducción de excepciones a HTTP (en el controller)
| Excepción Python | HTTP |
|---|---|
| `ValueError` | 400 |
| `PermissionError` | 403 |
| `LookupError` | 404 |
| cualquier otra | 500 |

Detalle de error siempre como `{ "estado", "mensaje", "detalle" }` dentro de `detail`.

### 4.7 FastAPI
```python
app = FastAPI(
    title="API Genérica CRUD",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url="/redoc",
    openapi_url="/swagger/v1/swagger.json",
)
```
CORS con `allow_origins=["*"]`, `allow_methods=["*"]`, `allow_headers=["*"]`.
Router con `prefix="/api"`, `tags=["Entidades"]`.

## 5. Dockerfile

1. `FROM python:3.12-slim`.
2. Instalar el driver ODBC de Microsoft (repositorio apt de Microsoft para Debian 12,
   `ACCEPT_EULA=Y apt-get install msodbcsql18 unixodbc`).
3. `COPY requirements.txt` + `pip install` **antes** de copiar el código
   (aprovecha la caché de capas).
4. `CMD uvicorn main:app --host 0.0.0.0 --port 8011`
   (en desarrollo, docker-compose lo sobreescribe agregando `--reload` y monta
   `./api_generica:/app` para recarga en caliente).

## 6. Convenciones

- Todo en **español**: nombres de archivos, clases, funciones, docstrings y comentarios.
- Comentarios didácticos: cada archivo abre con un docstring que explica su papel;
  los bloques se separan con líneas `# ====`.
- snake_case para archivos/funciones, PascalCase para clases, prefijo `i_`/`I` para contratos.
