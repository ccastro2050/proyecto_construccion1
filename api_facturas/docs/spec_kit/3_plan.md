# Plan técnico — API Facturas

> **Documento 3 de 8** del spec kit: **CÓMO** construir lo especificado en
> [2_spec.md](2_spec.md), sin depender de ningún otro proyecto. El porqué de cada
> decisión: [4_research.md](4_research.md). Modelo de datos: [5_data_model.md](5_data_model.md) ·
> endpoints: [6_contracts.md](6_contracts.md) · orden de trabajo: [8_tasks.md](8_tasks.md).

---

## 1. Stack

| Pieza | Elección | Por qué |
|---|---|---|
| Lenguaje | Python 3.12 | Imagen base `python:3.12-slim` |
| Framework web | FastAPI ≥ 0.100 | Async nativo, Swagger automático, validación Pydantic |
| Servidor | uvicorn[standard] ≥ 0.22 | Servidor ASGI estándar |
| Acceso a datos | SQLAlchemy 2 async (`sqlalchemy[asyncio]` + `greenlet`) | `text()` + parámetros nombrados unifica los 3 motores (sin ORM declarativo) |
| Driver PostgreSQL | asyncpg ≥ 0.28 | Async puro |
| Driver MySQL/MariaDB | aiomysql ≥ 0.2 (+ `cryptography` ≥ 42 para auth sha256 de MySQL 8) | Async puro |
| Driver SQL Server | aioodbc ≥ 0.5 + **msodbcsql18** (paquete del SO, via apt) | SQL Server solo habla ODBC |
| Configuración | pydantic ≥ 2, pydantic-settings ≥ 2, python-dotenv ≥ 1 | Variables con prefijo `DB_` desde entorno o `.env` |
| Contraseñas | bcrypt ≥ 4 (passlib ≥ 1.7.4 declarado por compatibilidad) | Hash de 60 caracteres, costo 12 |

`requirements.txt` = exactamente esa lista.

### Dockerfile

```dockerfile
FROM python:3.12-slim
# Driver ODBC de Microsoft (es del SO, no de pip): clave + repo Debian 12 + msodbcsql18
RUN apt-get update && apt-get install -y --no-install-recommends curl gnupg2 ca-certificates \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 unixodbc \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
```

En desarrollo: `uvicorn main:app --port 8002 --reload` (o en compose, montar el
código como volumen y agregar `--reload` al command).

## 2. Estructura de carpetas (el "corte vertical" por entidad)

```
api_facturas/
├── Dockerfile · requirements.txt · .gitignore (venv/, __pycache__/, *.pyc, .env)
├── config.py                    # pydantic-settings (§3)
├── main.py                      # app + registro de los 13 routers (§8)
├── models/                      # 12 modelos Pydantic — ver 5_data_model.md §5
│   └── __init__.py              # exporta las 12 clases + MODELOS_POR_TABLA
├── controllers/                 # 12 específicos + entidades_controller.py
├── servicios/
│   ├── abstracciones/           # i_servicio_<entidad>.py ×12 + i_servicio_crud.py + i_proveedor_conexion.py
│   ├── conexion/proveedor_conexion.py
│   ├── utilidades/encriptacion_bcrypt.py
│   ├── servicio_<entidad>.py    # ×12
│   ├── servicio_crud.py         # para el controller genérico
│   └── fabrica_repositorios.py  # 13 diccionarios + 13 funciones crear_*
├── repositorios/
│   ├── abstracciones/           # i_repositorio_<entidad>.py ×12 + i_repositorio_lectura_tabla.py
│   ├── base_repositorio_postgresql.py      # TODO el SQL PostgreSQL vive aquí
│   ├── base_repositorio_mysql_mariadb.py
│   ├── base_repositorio_sqlserver.py
│   └── <entidad>/               # ×12, cada una con 3 archivos:
│       └── repositorio_<entidad>_{postgresql|mysql_mariadb|sqlserver}.py
└── database/bdfacturas_postgres.sql   # DDL + datos + trigger + SPs (5_data_model.md)
```

Conteo: 12 modelos · 13 controllers · 13 servicios · 13 interfaces de servicio ·
3 bases + 36 repositorios concretos · 13 interfaces de repositorio · 1 fábrica ·
1 proveedor de conexión · 1 utilidad BCrypt. `__init__.py` en TODAS las carpetas
de paquete (los subpaquetes de entidad reexportan sus 3 clases).

**Flujo de una petición:**
```
HTTP → <entidad>_controller  (valida con Pydantic, traduce excepciones a HTTP)
     → crear_servicio_<entidad>()   [fábrica]
     → Servicio<Entidad>            (valida argumentos, normaliza)
     → Repositorio<Entidad><Motor>  (delega en su clase base)
     → Base<Motor>                  (arma y ejecuta SQL del dialecto)
     → AsyncEngine → BD
```
Regla de dependencias (SOLID): el controller solo conoce la fábrica y el
servicio; el servicio solo conoce la **interfaz** del repositorio; solo la
fábrica conoce las clases concretas.

## 3. Configuración (`config.py`)

```python
def get_environment() -> str:
    return os.getenv("ENVIRONMENT", "production").lower()

def get_env_file() -> str | tuple[str, str]:
    # development carga .env + .env.development (el segundo sobrescribe)
    ...

class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=get_env_file(),
        env_file_encoding='utf-8', env_prefix='DB_', extra='ignore')
    provider: str = Field(default='sqlserver')
    sqlserver: str = Field(default='')
    sqlserverexpress: str = Field(default='')
    localdb: str = Field(default='')
    postgres: str = Field(default='')
    mysql: str = Field(default='')
    mariadb: str = Field(default='')

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=get_env_file(),
        env_file_encoding='utf-8', extra='ignore')
    debug: bool = Field(default=False, alias='DEBUG')
    environment: str = Field(default_factory=get_environment)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

@lru_cache()
def get_settings() -> Settings: return Settings()
```

Nota: por el `lru_cache`, cambiar `DB_PROVIDER` exige reiniciar el proceso.

Cadenas de conexión aceptadas (la normalización la hacen las bases, §5):
```
DB_POSTGRES=postgresql+asyncpg://usuario:clave@host:5432/bdfacturas_postgres_local
DB_MARIADB=mysql+aiomysql://usuario:clave@host:3306/bdfacturas_mariadb_local      (o estilo C# Server=...;Database=...)
DB_SQLSERVER=mssql+aioodbc://usuario:clave@host:1433/bd?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes   (o cadena ODBC cruda)
```

### Proveedor de conexión

```python
class IProveedorConexion(Protocol):
    @property
    def proveedor_actual(self) -> str: ...
    def obtener_cadena_conexion(self) -> str: ...

class ProveedorConexion:
    def __init__(self, settings: Settings | None = None):
        self._settings = settings or get_settings()
    @property
    def proveedor_actual(self) -> str:
        return self._settings.database.provider.lower().strip()
    def obtener_cadena_conexion(self) -> str:
        # dict proveedor→cadena; ValueError con opciones si no existe;
        # ValueError "Verificar DB_<PROVIDER> en .env" si está vacía
```

## 4. Utilidad BCrypt (`servicios/utilidades/encriptacion_bcrypt.py`)

Funciones puras con `import bcrypt`:

```python
COSTO_POR_DEFECTO: int = 12

def encriptar(valor_original: str, costo: int = COSTO_POR_DEFECTO) -> str:
    # valida no-vacío y 4 <= costo <= 31; gensalt(rounds=costo) + hashpw → str de 60 chars

def verificar(valor_original: str, hash_existente: str) -> bool:
    # checkpw; CUALQUIER excepción → False (hash malformado no rompe)
```

## 5. Clases base de repositorio (el corazón anti-duplicación)

Todo el SQL de cada motor vive en UNA clase
(`BaseRepositorioPostgreSQL`, `BaseRepositorioMysqlMariaDB`, `BaseRepositorioSqlServer`)
con la MISMA superficie:

**Constructor y engine:**
```python
def __init__(self, proveedor_conexion: IProveedorConexion):
    # ValueError si None; self._engine: AsyncEngine | None = None

async def _obtener_engine(self) -> AsyncEngine:
    # lazy: create_async_engine(cadena, echo=False) la primera vez, luego cachea
```

**Helpers de tipos** (los valores llegan como texto por la URL; hay que
convertirlos al tipo real de la columna):
- `_detectar_tipo_columna(tabla, esquema, columna)` → consulta
  `information_schema.columns` (devuelve `None` si falla).
- `_convertir_valor(valor: str, tipo)` → `int`, `Decimal`, `float`, `bool`
  (acepta `'true','1','yes','si','t'`), `UUID`, `date`, `datetime`
  (`fromisoformat` con `Z`→`+00:00`), `time`; si no puede, devuelve el string.
- `_es_fecha_sin_hora(valor)` (formato `YYYY-MM-DD`) y `_extraer_solo_fecha(valor)`.
- `_serializar_valor(valor)` → `datetime/date`→ISO, `Decimal`→float, `UUID`→str
  (hace las filas JSON-serializables).

**Las 6 operaciones**, públicas Y con alias protegido `_` (los repos de entidad
usan `_`; el `ServicioCrud` genérico usa las públicas — en el código original
faltaban las públicas y el controller genérico daba 500):

```python
obtener_filas(tabla, esquema=None, limite=None) -> list[dict]
obtener_por_clave(tabla, clave, valor, esquema=None) -> list[dict]
    # caso especial: columna TIMESTAMP + valor YYYY-MM-DD → WHERE CAST(col AS DATE) = :valor
crear(tabla, datos, esquema=None, campos_encriptar=None) -> bool          # rowcount > 0
actualizar(tabla, clave, valor_clave, datos, esquema=None, campos_encriptar=None) -> int
eliminar(tabla, clave, valor_clave, esquema=None) -> int
obtener_hash_contrasena(tabla, campo_usuario, campo_contrasena, valor_usuario, esquema=None) -> str | None
```

`campos_encriptar` (CSV, case-insensitive): los valores de esas columnas pasan
por `encriptar()` antes del INSERT/UPDATE.

Reglas de SQL: **valores siempre como parámetros nombrados `:x`** de
`sqlalchemy.text()` (nunca concatenados); identificadores (tabla/columna/esquema)
interpolados con las comillas del dialecto; lecturas con `engine.connect()`,
escrituras con `engine.begin()` (transacción); errores envueltos:
`raise RuntimeError(f"Error <Motor> al <verbo> '<esq>.<tabla>': {ex}") from ex`;
`ValueError` si tabla/clave/valor/datos llegan vacíos. Sin `RETURNING`/`OUTPUT`:
el POST no devuelve la PK generada (decisión del original; mejorarlo es opcional).

**Diferencias por dialecto (TODA la diferencia vive aquí):**

| Aspecto | PostgreSQL | MySQL/MariaDB | SQL Server |
|---|---|---|---|
| Comillas identificador | `"tabla"` | `` `tabla` `` | `[tabla]` |
| Limitar filas | `LIMIT :limite` | `LIMIT :limite` | `SELECT TOP ({n})` (interpolado; validar int) |
| Esquema default | `public` | ninguno (usa la BD de la conexión) | `dbo` |
| Normalización de cadena | ninguna (URL directa) | `_convertir_cadena_csharp_a_sqlalchemy()`: `Server=x;Port=y;Database=z;User=u;Password=p` → `mysql+aiomysql://u:p@x:y/z` (defaults localhost/3306/root) | `_convertir_odbc_a_sqlalchemy()`: si no empieza por `mssql+` → `mssql+aioodbc:///?odbc_connect={quote_plus(cadena)}` |

## 6. Repositorios e interfaces por entidad

Interfaz (`typing.Protocol`, tipado estructural — los concretos NO heredan de ella):

```python
class IRepositorioPersona(Protocol):
    async def obtener_todos(self, esquema=None, limite=None) -> list[dict[str, Any]]: ...
    async def obtener_por_codigo(self, codigo: str, esquema=None) -> list[dict[str, Any]]: ...
    async def crear(self, datos: dict[str, Any], esquema=None) -> bool: ...
    async def actualizar(self, codigo: str, datos: dict[str, Any], esquema=None) -> int: ...
    async def eliminar(self, codigo: str, esquema=None) -> int: ...
```

Repositorio concreto = ~35 líneas de constantes + delegación:

```python
class RepositorioPersonaPostgreSQL(BaseRepositorioPostgreSQL):
    TABLA = "persona"
    CLAVE_PRIMARIA = "codigo"
    async def obtener_todos(self, esquema=None, limite=None):
        return await self._obtener_filas(self.TABLA, esquema, limite)
    async def obtener_por_codigo(self, codigo, esquema=None):
        return await self._obtener_por_clave(self.TABLA, self.CLAVE_PRIMARIA, str(codigo), esquema)
    # crear / actualizar / eliminar → misma delegación
```

Las 3 variantes de cada entidad son idénticas salvo la clase base. Ajustes por entidad:
- **usuario**: `CAMPOS_ENCRIPTAR = "contrasena"` (se pasa en crear/actualizar) +
  método extra `obtener_hash_contrasena(email, esquema=None)`.
- **productosporfactura**: sin `actualizar`; método `obtener_por_factura(fknumfactura)`;
  su interfaz refleja eso.
- **rol_usuario**: sin `actualizar`; `obtener_por_email(fkemail)` y `obtener_por_rol(fkidrol)`.
- **rutarol**: sin `actualizar`; `obtener_por_ruta(ruta)` y `obtener_por_rol(rol)`.
- El DELETE de las 3 tablas puente: implementar según la decisión tomada
  (spec RF2 — fiel: filtra solo el primer segmento; corregido: WHERE por ambas columnas).

También: `i_repositorio_lectura_tabla.py` (`IRepositorioLecturaTabla(Protocol)`)
con las 6 operaciones genéricas que consume `ServicioCrud`, y alias en
`repositorios/__init__.py`:
`RepositorioLecturaPostgreSQL = BaseRepositorioPostgreSQL` (ídem los otros dos).

## 7. Servicios y fábrica

`Servicio<Entidad>` — inyección por constructor, sin reglas de negocio pesadas:

```python
class ServicioPersona:
    def __init__(self, repositorio):
        if repositorio is None: raise ValueError("repositorio no puede ser None.")
        self._repo = repositorio
    # listar / obtener_por_codigo / crear / actualizar / eliminar:
    #   - ValueError con mensaje en español si un argumento viene vacío
    #   - normaliza: esquema.strip() o None; limite > 0 o None
    #   - delega en el repo
```

`ServicioUsuario` agrega `verificar_contrasena(email, contrasena, esquema=None)
-> tuple[int, str]`: obtiene el hash con el repo y devuelve
`(200, "Contraseña válida.")` / `(401, "Contraseña incorrecta.")` /
`(404, "Usuario no encontrado.")` usando `verificar()`.

`ServicioCrud` (genérico): las 6 operaciones sobre `IRepositorioLecturaTabla`
con las mismas validaciones, más `verificar_contrasena` parametrizado por
campo de usuario/contraseña.

**Fábrica** (`fabrica_repositorios.py`) — patrón Factory con diccionarios:

```python
def _obtener_proveedor():
    proveedor = ProveedorConexion()
    return proveedor, proveedor.proveedor_actual

_REPOS_PERSONA = {   # mismas 7 claves en los 13 diccionarios
    "sqlserver": RepositorioPersonaSqlServer, "sqlserverexpress": RepositorioPersonaSqlServer,
    "localdb": RepositorioPersonaSqlServer,
    "postgres": RepositorioPersonaPostgreSQL, "postgresql": RepositorioPersonaPostgreSQL,
    "mysql": RepositorioPersonaMysqlMariaDB, "mariadb": RepositorioPersonaMysqlMariaDB,
}

def crear_servicio_persona() -> ServicioPersona:
    proveedor, nombre = _obtener_proveedor()
    repo = _crear_repo_entidad(_REPOS_PERSONA, proveedor, nombre)   # ValueError si no existe
    return ServicioPersona(repo)
```

12 funciones `crear_servicio_<entidad>()` + `crear_repositorio_lectura()` /
`crear_servicio_crud()` para el genérico. Cada handler llama a su `crear_*()`
dentro del cuerpo (sin `Depends`). *Mejora opcional:* cachear engine por
proveedor a nivel de módulo (el original crea un engine por petición).

## 8. Controllers y main.py

Patrón de handler (los formatos exactos están en [6_contracts.md](6_contracts.md)):

```python
router = APIRouter(prefix="/api/persona", tags=["Persona"])

@router.get("/")
async def listar(esquema: str | None = Query(default=None),
                 limite: int | None = Query(default=None)):
    try:
        servicio = crear_servicio_persona()
        filas = await servicio.listar(esquema, limite)
        if len(filas) == 0:
            return Response(status_code=204)
        return {"tabla": "persona", "total": len(filas), "datos": filas}
    except HTTPException: raise          # ¡SIEMPRE antes de los genéricos!
    except ValueError as ex:  raise HTTPException(400, detail={"estado":400,"mensaje":"Parámetros inválidos.","detalle":str(ex)})
    except Exception as ex:   raise HTTPException(500, detail={"estado":500,"mensaje":"Error interno del servidor.","detalle":str(ex)})
```

- PUT: `datos = modelo.model_dump(exclude={"<pk>"})` (no se actualiza la clave).
- `ruta_controller`: `{valor_ruta:path}` en GET/PUT/DELETE.
- Tablas puente: sin PUT; búsquedas secundarias como endpoints GET adicionales.
- `usuario_controller`: agrega `POST /verificar-contrasena` mapeando la tupla
  del servicio a 200/401/404.
- `entidades_controller` (genérico, prefix `/api`): 6 endpoints con body
  `dict[str, Any]` y mapeo `ValueError`→400, `PermissionError`→403,
  `LookupError`→404, resto→500.

`main.py`:

```python
app = FastAPI(title="API Facturas CRUD",
              description="API REST para operaciones CRUD sobre la base de datos de facturas.",
              version="1.0.0")          # /docs y /redoc por defecto (NO /swagger)

# (mejora RNF6) CORSMiddleware con allow_origins=["*"] si habrá clientes de navegador

# 12 routers específicos PRIMERO (FastAPI resuelve por orden de registro)...
from controllers.persona_controller import router as persona_router
# ... productosporfactura se importa como detalle_router
app.include_router(persona_router)
# ...los 11 restantes...
app.include_router(entidades_router)    # el genérico DE ÚLTIMO: atrapa /api/{tabla} restante

@app.get("/", tags=["Root"])
async def root():
    return {"mensaje": "API Facturas CRUD activa.", "docs": "/docs", "redoc": "/redoc"}
```

## 9. Convenciones

- **Español en todo**: clases, métodos, variables, docstrings, mensajes.
- Archivos snake_case; clases PascalCase; interfaces `i_`/`I` con `Protocol`.
- Sufijos de motor: `_postgresql` / `_mysql_mariadb` / `_sqlserver`
  (clases: `PostgreSQL` / `MysqlMariaDB` / `SqlServer`).
- Constantes de clase en MAYÚSCULAS: `TABLA`, `CLAVE_PRIMARIA`, `CAMPOS_ENCRIPTAR`.
- Rutas HTTP kebab-case con dos palabras (`/api/rol-usuario`,
  `/verificar-contrasena`); `rutarol` y `productosporfactura` van pegadas.
- Claves JSON de respuesta: `estado`, `mensaje`, `tabla`, `total`, `datos`,
  `filtro`, y en camelCase `filasAfectadas` / `filasEliminadas` (consumidores
  externos dependen de estos nombres exactos).
- Cada archivo abre con docstring didáctico (nombre — propósito — conceptos);
  separadores `# ================` entre secciones.
