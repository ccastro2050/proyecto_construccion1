# API Facturas CRUD

API REST construida con **FastAPI** y **Python 3.11+** que implementa operaciones CRUD completas sobre una base de datos de facturación. Soporta **PostgreSQL**, **SQL Server** y **MySQL/MariaDB** de forma simultánea, seleccionando el motor desde una variable de entorno.

```
uvicorn main:app --reload
```

---

## Tabla de contenido

- [Arquitectura general](#arquitectura-general)
- [Flujo de una petición](#flujo-de-una-petición)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Modelo de datos (12 tablas)](#modelo-de-datos-12-tablas)
- [Capas en detalle](#capas-en-detalle)
  - [1. Controllers (Presentación)](#1-controllers-presentación)
  - [2. Servicios (Lógica de negocio)](#2-servicios-lógica-de-negocio)
  - [3. Repositorios (Acceso a datos)](#3-repositorios-acceso-a-datos)
  - [4. Modelos Pydantic (Validación)](#4-modelos-pydantic-validación)
  - [5. Configuración y conexión](#5-configuración-y-conexión)
- [Endpoints disponibles](#endpoints-disponibles)
- [Patrones de diseño utilizados](#patrones-de-diseño-utilizados)
- [Requisitos previos](#requisitos-previos)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Configuración del archivo .env](#configuración-del-archivo-env)
- [Encriptación de contraseñas (BCrypt)](#encriptación-de-contraseñas-bcrypt)
- [Documentación del tutorial](#documentación-del-tutorial)

---

## Arquitectura general

El proyecto sigue una **arquitectura en 3 capas** donde cada capa tiene una responsabilidad única y se comunica solo con la capa inmediatamente inferior:

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENTE (HTTP)                        │
│              Postman / Frontend / curl                   │
└──────────────────────┬──────────────────────────────────┘
                       │ JSON
┌──────────────────────▼──────────────────────────────────┐
│              CAPA 1: CONTROLLERS                        │
│                                                         │
│  persona_controller.py    empresa_controller.py   ...   │
│  (FastAPI Routers — reciben HTTP, retornan JSON)        │
│                                                         │
│  Responsabilidad:                                       │
│  - Definir endpoints (GET, POST, PUT, DELETE)           │
│  - Validar datos con modelos Pydantic                   │
│  - Delegar al servicio correspondiente                  │
│  - Formatear respuestas HTTP y códigos de estado        │
└──────────────────────┬──────────────────────────────────┘
                       │ Objetos Python
┌──────────────────────▼──────────────────────────────────┐
│              CAPA 2: SERVICIOS                          │
│                                                         │
│  servicio_persona.py    servicio_empresa.py    ...      │
│  (Lógica de negocio — validación, normalización)        │
│                                                         │
│  Responsabilidad:                                       │
│  - Validar reglas de negocio                            │
│  - Normalizar entradas (esquema, límite)                │
│  - Coordinar operaciones (ej: encriptar contraseña)     │
│  - Delegar al repositorio correspondiente               │
└──────────────────────┬──────────────────────────────────┘
                       │ Objetos Python
┌──────────────────────▼──────────────────────────────────┐
│              CAPA 3: REPOSITORIOS                       │
│                                                         │
│  RepositorioPersonaPostgreSQL                           │
│  RepositorioPersonaSqlServer                            │
│  RepositorioPersonaMysqlMariaDB                         │
│  (Acceso a datos — SQL, conexión, serialización)        │
│                                                         │
│  Responsabilidad:                                       │
│  - Construir consultas SQL parametrizadas               │
│  - Ejecutar queries contra la BD                        │
│  - Serializar resultados a diccionarios Python          │
│  - Manejar tipos de datos específicos del motor         │
└──────────────────────┬──────────────────────────────────┘
                       │ SQL
┌──────────────────────▼──────────────────────────────────┐
│              BASE DE DATOS                              │
│                                                         │
│    PostgreSQL  │  SQL Server  │  MySQL / MariaDB        │
└─────────────────────────────────────────────────────────┘
```

### Principio clave: cada capa es específica por entidad

Toda la cadena desde el controller hasta el repositorio es **100% específica por entidad**. No hay servicios ni repositorios genéricos en el flujo principal. Cada entidad tiene su propia interfaz, su propia implementación y su propio servicio:

```
PersonaController ──→ ServicioPersona ──→ IRepositorioPersona ──→ RepositorioPersonaPostgreSQL
                                                                ──→ RepositorioPersonaSqlServer
                                                                ──→ RepositorioPersonaMysqlMariaDB
```

---

## Flujo de una petición

### Ejemplo: `GET /api/persona/P001`

```
1. El cliente envía:  GET http://localhost:8000/api/persona/P001

2. FastAPI enruta la petición a persona_controller.py
   → función: obtener_persona(codigo="P001")

3. El controller llama a la fábrica:
   → servicio = crear_servicio_persona()
   → La fábrica lee DB_PROVIDER del .env (ej: "postgres")
   → Crea RepositorioPersonaPostgreSQL
   → Lo inyecta en ServicioPersona

4. El controller delega al servicio:
   → filas = await servicio.obtener_por_codigo("P001")

5. El servicio valida la entrada:
   → Verifica que el código no esté vacío
   → Delega al repositorio

6. El repositorio ejecuta SQL:
   → SELECT * FROM persona WHERE codigo = $1
   → Parámetro: "P001"
   → Serializa el resultado a dict

7. El resultado sube por las capas:
   → Repositorio retorna: [{"codigo": "P001", "nombre": "Juan", ...}]
   → Servicio retorna la lista tal cual
   → Controller retorna JSON con status 200

8. Respuesta al cliente:
   {
     "tabla": "persona",
     "total": 1,
     "datos": [{"codigo": "P001", "nombre": "Juan", ...}]
   }
```

### Ejemplo: `POST /api/usuario/` (con encriptación)

```
1. El cliente envía:
   POST http://localhost:8000/api/usuario/
   Body: {"email": "ana@test.com", "contrasena": "123456"}

2. FastAPI valida el body con el modelo Pydantic Usuario:
   → email: str ✓
   → contrasena: str ✓

3. El controller delega:
   → datos = usuario.model_dump()
   → servicio = crear_servicio_usuario()
   → creado = await servicio.crear(datos)

4. El servicio valida y delega al repositorio

5. El repositorio detecta que "contrasena" es un campo a encriptar:
   → CAMPOS_ENCRIPTAR = "contrasena"
   → Encripta "123456" → "$2b$12$xR3k..." (hash BCrypt de 60 chars)
   → INSERT INTO usuario (email, contrasena) VALUES ($1, $2)

6. Respuesta: {"estado": 200, "mensaje": "Usuario creado exitosamente."}
```

---

## Estructura del proyecto

```
ApiFacturasFastApi_Crud/
│
├── main.py                              # Punto de entrada FastAPI
├── config.py                            # Configuración centralizada (pydantic-settings)
├── requirements.txt                     # Dependencias del proyecto
├── .env                                 # Variables de entorno (no versionado)
├── .gitignore
│
├── models/                              # Modelos Pydantic (validación de datos)
│   ├── __init__.py                      #   Diccionario MODELOS_POR_TABLA
│   ├── persona.py                       #   PK: codigo (str)
│   ├── empresa.py                       #   PK: codigo (str)
│   ├── cliente.py                       #   PK: id (int)
│   ├── vendedor.py                      #   PK: id (int)
│   ├── producto.py                      #   PK: codigo (str)
│   ├── factura.py                       #   PK: numero (int)
│   ├── productosporfactura.py           #   PK compuesta: fknumfactura + fkcodproducto
│   ├── usuario.py                       #   PK: email (str) — contraseña BCrypt
│   ├── rol.py                           #   PK: id (int)
│   ├── rol_usuario.py                   #   PK compuesta: usuario + rol
│   ├── ruta.py                          #   PK: ruta (str)
│   └── rutarol.py                       #   PK compuesta: ruta + rol
│
├── controllers/                         # Endpoints HTTP (FastAPI Routers)
│   ├── __init__.py
│   ├── persona_controller.py            #   /api/persona/
│   ├── empresa_controller.py            #   /api/empresa/
│   ├── cliente_controller.py            #   /api/cliente/
│   ├── vendedor_controller.py           #   /api/vendedor/
│   ├── producto_controller.py           #   /api/producto/
│   ├── factura_controller.py            #   /api/factura/
│   ├── productosporfactura_controller.py#   /api/productosporfactura/
│   ├── usuario_controller.py            #   /api/usuario/ + verificar-contrasena
│   ├── rol_controller.py                #   /api/rol/
│   ├── rol_usuario_controller.py        #   /api/rolusuario/
│   ├── ruta_controller.py               #   /api/ruta/
│   ├── rutarol_controller.py            #   /api/rutarol/
│   └── entidades_controller.py          #   /api/{tabla}/ (genérico, retrocompatibilidad)
│
├── servicios/                           # Lógica de negocio
│   ├── abstracciones/                   #   Interfaces (Protocol)
│   │   ├── i_servicio_persona.py
│   │   ├── i_servicio_empresa.py
│   │   ├── i_servicio_cliente.py
│   │   ├── i_servicio_vendedor.py
│   │   ├── i_servicio_producto.py
│   │   ├── i_servicio_factura.py
│   │   ├── i_servicio_productosporfactura.py
│   │   ├── i_servicio_usuario.py        #   + verificar_contrasena()
│   │   ├── i_servicio_rol.py
│   │   ├── i_servicio_rol_usuario.py
│   │   ├── i_servicio_ruta.py
│   │   ├── i_servicio_rutarol.py
│   │   ├── i_servicio_crud.py           #   Interfaz del servicio genérico
│   │   └── i_proveedor_conexion.py      #   Interfaz del proveedor de conexión
│   ├── conexion/
│   │   └── proveedor_conexion.py        #   Lee DB_PROVIDER y cadenas de conexión
│   ├── utilidades/
│   │   └── encriptacion_bcrypt.py       #   Hashear y verificar contraseñas
│   ├── servicio_persona.py
│   ├── servicio_empresa.py
│   ├── servicio_cliente.py
│   ├── servicio_vendedor.py
│   ├── servicio_producto.py
│   ├── servicio_factura.py
│   ├── servicio_productosporfactura.py
│   ├── servicio_usuario.py              #   Incluye verificar_contrasena()
│   ├── servicio_rol.py
│   ├── servicio_rol_usuario.py
│   ├── servicio_ruta.py
│   ├── servicio_rutarol.py
│   ├── servicio_crud.py                 #   Servicio genérico (retrocompatibilidad)
│   └── fabrica_repositorios.py          #   Factory: crea servicio+repo según .env
│
├── repositorios/                        # Acceso a datos (SQL)
│   ├── __init__.py                      #   Exporta bases + aliases
│   ├── abstracciones/                   #   Interfaces de repositorios
│   │   ├── i_repositorio_persona.py
│   │   ├── i_repositorio_empresa.py
│   │   ├── i_repositorio_cliente.py
│   │   ├── i_repositorio_vendedor.py
│   │   ├── i_repositorio_producto.py
│   │   ├── i_repositorio_factura.py
│   │   ├── i_repositorio_productosporfactura.py
│   │   ├── i_repositorio_usuario.py     #   + obtener_hash_contrasena()
│   │   ├── i_repositorio_rol.py
│   │   ├── i_repositorio_rol_usuario.py
│   │   ├── i_repositorio_ruta.py
│   │   ├── i_repositorio_rutarol.py
│   │   └── i_repositorio_lectura_tabla.py  # Interfaz genérica
│   ├── base_repositorio_postgresql.py   #   Clase base PostgreSQL (métodos _protegidos)
│   ├── base_repositorio_sqlserver.py    #   Clase base SQL Server
│   ├── base_repositorio_mysql_mariadb.py#   Clase base MySQL/MariaDB
│   ├── persona/                         #   3 implementaciones por entidad
│   │   ├── __init__.py
│   │   ├── repositorio_persona_postgresql.py
│   │   ├── repositorio_persona_sqlserver.py
│   │   └── repositorio_persona_mysql_mariadb.py
│   ├── empresa/                         #   (misma estructura)
│   ├── cliente/
│   ├── vendedor/
│   ├── producto/
│   ├── factura/
│   ├── productosporfactura/
│   ├── usuario/
│   ├── rol/
│   ├── rol_usuario/
│   ├── ruta/
│   └── rutarol/
│
└── docs/                                # Documentación del tutorial (.docx)
    ├── Parte_1_Conceptos_Fundamentales.docx
    ├── Parte_2_Crear_Proyecto_y_Configuracion.docx
    ├── Parte_3_*.docx                   #   Capa de datos (4 documentos)
    ├── Parte_4_*.docx                   #   Capa de negocio (2 documentos)
    ├── Parte_5_*.docx                   #   Modelos y controllers (4 documentos)
    ├── Parte_6_Main_Punto_de_Entrada.docx
    └── Parte_7_Repositorios_y_Servicios_Especificos.docx
```

---

## Modelo de datos (12 tablas)

La base de datos `bdfacturas` contiene 12 tablas organizadas en 3 grupos:

### Entidades principales

| Tabla | Clave primaria | Tipo | Descripción |
|-------|---------------|------|-------------|
| `persona` | `codigo` | `str` | Personas naturales |
| `empresa` | `codigo` | `str` | Personas jurídicas |
| `cliente` | `id` | `int` | Clientes (referencia persona o empresa) |
| `vendedor` | `id` | `int` | Vendedores |
| `producto` | `codigo` | `str` | Catálogo de productos |

### Facturación

| Tabla | Clave primaria | Tipo | Descripción |
|-------|---------------|------|-------------|
| `factura` | `numero` | `int` | Encabezado de factura |
| `productosporfactura` | `fknumfactura` + `fkcodproducto` | compuesta | Detalle (productos por factura) |

### Seguridad y permisos

| Tabla | Clave primaria | Tipo | Descripción |
|-------|---------------|------|-------------|
| `usuario` | `email` | `str` | Usuarios con contraseña BCrypt |
| `rol` | `id` | `int` | Roles del sistema |
| `rol_usuario` | `usuario` + `rol` | compuesta | Asignación de roles a usuarios |
| `ruta` | `ruta` | `str` | Rutas/endpoints protegidos |
| `rutarol` | `ruta` + `rol` | compuesta | Permisos de rol sobre rutas |

---

## Capas en detalle

### 1. Controllers (Presentación)

Cada controller es un **APIRouter de FastAPI** que define los endpoints HTTP para su entidad. Los controllers **no contienen lógica de negocio**, solo:

- Reciben la petición HTTP
- Validan el body con el modelo Pydantic
- Delegan al servicio específico
- Formatean la respuesta JSON

**Ejemplo simplificado** ([persona_controller.py](controllers/persona_controller.py)):

```python
from servicios.fabrica_repositorios import crear_servicio_persona
from models.persona import Persona

router = APIRouter(prefix="/api/persona", tags=["Persona"])

@router.get("/{codigo}")
async def obtener_persona(codigo: str, esquema: str | None = Query(default=None)):
    servicio = crear_servicio_persona()            # Fábrica crea servicio + repo
    filas = await servicio.obtener_por_codigo(codigo, esquema)   # Sin strings de tabla
    return {"tabla": "persona", "total": len(filas), "datos": filas}
```

**Controller genérico** ([entidades_controller.py](controllers/entidades_controller.py)):
Existe un controller genérico en `/api/{tabla}` que acepta cualquier nombre de tabla como parámetro. Se mantiene por retrocompatibilidad pero los controllers específicos tienen prioridad al registrarse primero en `main.py`.

---

### 2. Servicios (Lógica de negocio)

Cada servicio recibe un repositorio inyectado y aplica reglas de negocio antes de delegar:

- Validación de entradas (campos vacíos, valores nulos)
- Normalización de esquema y límite
- Coordinación de operaciones complejas (encriptar contraseña + verificar)

**Ejemplo** ([servicio_persona.py](servicios/servicio_persona.py)):

```python
class ServicioPersona:
    def __init__(self, repositorio):
        self._repo = repositorio

    async def listar(self, esquema=None, limite=None):
        esquema_norm = esquema.strip() if esquema and esquema.strip() else None
        limite_norm = limite if limite and limite > 0 else None
        return await self._repo.obtener_todos(esquema_norm, limite_norm)

    async def obtener_por_codigo(self, codigo, esquema=None):
        if not codigo or not codigo.strip():
            raise ValueError("El código no puede estar vacío.")
        return await self._repo.obtener_por_codigo(codigo, esquema_norm)
```

**Caso especial** — `ServicioUsuario` incluye verificación de credenciales:

```python
async def verificar_contrasena(self, email, contrasena, esquema=None):
    hash_almacenado = await self._repo.obtener_hash_contrasena(email, esquema)
    if hash_almacenado is None:
        return (404, "Usuario no encontrado.")
    if verificar(contrasena, hash_almacenado):  # BCrypt
        return (200, "Contraseña válida.")
    return (401, "Contraseña incorrecta.")
```

---

### 3. Repositorios (Acceso a datos)

Los repositorios se organizan en dos niveles:

**Clases base por motor** — Contienen toda la lógica SQL reutilizable como métodos protegidos (`_`):

| Clase base | Motor | Driver async |
|------------|-------|--------------|
| `BaseRepositorioPostgreSQL` | PostgreSQL | `asyncpg` vía SQLAlchemy |
| `BaseRepositorioSqlServer` | SQL Server | `aioodbc` vía SQLAlchemy |
| `BaseRepositorioMysqlMariaDB` | MySQL / MariaDB | `aiomysql` vía SQLAlchemy |

Métodos protegidos disponibles en cada base:
- `_obtener_filas(tabla, esquema, limite)` — SELECT *
- `_obtener_por_clave(tabla, clave, valor, esquema)` — SELECT WHERE
- `_crear(tabla, datos, esquema, campos_encriptar)` — INSERT
- `_actualizar(tabla, clave, valor, datos, esquema, campos_encriptar)` — UPDATE
- `_eliminar(tabla, clave, valor, esquema)` — DELETE
- `_obtener_hash_contrasena(tabla, campo_usuario, campo_contrasena, valor, esquema)`

**Repositorios específicos** — Heredan de la base del motor y llaman a los métodos protegidos con la tabla y PK fija:

```python
class RepositorioPersonaPostgreSQL(BaseRepositorioPostgreSQL):
    TABLA = "persona"
    CLAVE_PRIMARIA = "codigo"

    async def obtener_todos(self, esquema=None, limite=None):
        return await self._obtener_filas(self.TABLA, esquema, limite)

    async def obtener_por_codigo(self, codigo, esquema=None):
        return await self._obtener_por_clave(self.TABLA, self.CLAVE_PRIMARIA, str(codigo), esquema)

    async def crear(self, datos, esquema=None):
        return await self._crear(self.TABLA, datos, esquema)
```

Esto significa que el nombre de la tabla y la clave primaria **nunca salen del repositorio**. Las capas superiores no necesitan conocer estos detalles.

---

### 4. Modelos Pydantic (Validación)

Cada tabla tiene un modelo Pydantic que valida automáticamente los datos del body en los endpoints POST y PUT:

```python
# models/persona.py
class Persona(BaseModel):
    codigo: str
    nombre: str
    email: str | None = None
    telefono: str | None = None

# models/usuario.py
class Usuario(BaseModel):
    email: str           # PK
    contrasena: str      # Se encripta con BCrypt antes de guardar
```

FastAPI usa estos modelos para:
- Validar tipos de datos automáticamente
- Generar documentación OpenAPI (Swagger)
- Rechazar peticiones con datos inválidos (error 422)

---

### 5. Configuración y conexión

**`config.py`** usa `pydantic-settings` para leer variables del `.env`:

```python
class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='DB_')

    provider: str = 'sqlserver'      # DB_PROVIDER en .env
    postgres: str = ''               # DB_POSTGRES en .env
    sqlserver: str = ''              # DB_SQLSERVER en .env
    mysql: str = ''                  # DB_MYSQL en .env
```

**`ProveedorConexion`** lee `DB_PROVIDER` y entrega la cadena de conexión correspondiente.

**`fabrica_repositorios.py`** (Factory) — Es el punto central donde se conectan las capas. Lee el proveedor activo y crea el repositorio + servicio correctos:

```python
def crear_servicio_persona() -> ServicioPersona:
    proveedor, nombre = _obtener_proveedor()       # Lee DB_PROVIDER
    repo = _crear_repo_entidad(_REPOS_PERSONA, proveedor, nombre)  # Crea el repo del motor activo
    return ServicioPersona(repo)                    # Inyecta el repo en el servicio
```

Para cambiar de motor de BD, **solo se cambia `DB_PROVIDER` en el `.env`**. No se modifica ni una línea de código.

---

## Endpoints disponibles

### Controllers específicos (12 entidades)

Cada entidad expone estos endpoints (ejemplo con `persona`):

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/persona/` | Listar todas las personas |
| `GET` | `/api/persona/{codigo}` | Obtener persona por PK |
| `POST` | `/api/persona/` | Crear persona (body JSON) |
| `PUT` | `/api/persona/{codigo}` | Actualizar persona |
| `DELETE` | `/api/persona/{codigo}` | Eliminar persona |

**Parámetros query opcionales en todos los endpoints:**
- `esquema` — Esquema de la BD (si aplica)
- `limite` — Límite de registros (solo en GET de listado)

**Endpoints especiales:**

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/usuario/verificar-contrasena` | Verificar credenciales con BCrypt |
| `GET` | `/api/rolusuario/usuario/{usuario}` | Roles de un usuario |
| `GET` | `/api/productosporfactura/factura/{num}` | Productos de una factura |
| `GET` | `/api/rutarol/rol/{rol}` | Rutas asignadas a un rol |

### Controller genérico (retrocompatibilidad)

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/{tabla}` | Listar registros de cualquier tabla |
| `GET` | `/api/{tabla}/{clave}/{valor}` | Filtrar por clave-valor |
| `POST` | `/api/{tabla}` | Crear registro (body JSON libre) |
| `PUT` | `/api/{tabla}/{clave}/{valor}` | Actualizar registro |
| `DELETE` | `/api/{tabla}/{clave}/{valor}` | Eliminar registro |

### Documentación automática

| Ruta | Descripción |
|------|-------------|
| `/docs` | Swagger UI (interactivo) |
| `/redoc` | ReDoc (documentación legible) |
| `/` | Endpoint raíz de verificación |

---

## Patrones de diseño utilizados

| Patrón | Dónde se aplica | Para qué sirve |
|--------|----------------|-----------------|
| **Repository** | `repositorios/` | Abstraer el acceso a datos detrás de una interfaz. El servicio no sabe si usa PostgreSQL o MySQL |
| **Factory** | `fabrica_repositorios.py` | Crear el repositorio y servicio correctos según la configuración, sin que el controller lo decida |
| **Protocol (Interface)** | `abstracciones/` | Definir contratos con tipado estructural (duck typing). No requiere herencia explícita |
| **Template Method** | Base repositories | Las clases base definen el algoritmo SQL; las subclases solo fijan la tabla y PK |
| **Dependency Injection** | Servicios | El servicio recibe el repositorio por constructor, no lo crea internamente |
| **Singleton** | `config.py` (`@lru_cache`) | La configuración se lee una sola vez y se reutiliza en toda la aplicación |
| **Strategy** | Repositorios por motor | Cada motor de BD es una estrategia diferente con la misma interfaz |

---

## Requisitos previos

- **Python 3.11+** (usa sintaxis `str | None`)
- **pip** para instalar dependencias
- Al menos uno de estos motores de BD configurado:
  - **PostgreSQL 12+** con el driver `asyncpg`
  - **SQL Server 2017+** con ODBC Driver 17 instalado
  - **MySQL 8+** o **MariaDB 10.5+** con el driver `aiomysql`

---

## Instalación y ejecución

```bash
# 1. Clonar el repositorio
git clone https://github.com/ccastro2050/ApiFacturasFastApi_Crud.git
cd ApiFacturasFastApi_Crud

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar el archivo .env (ver sección siguiente)
# Copiar .env.example o crear .env con las cadenas de conexión

# 6. Ejecutar la API
uvicorn main:app --reload

# 7. Abrir en el navegador
# http://localhost:8000/docs  ← Swagger UI
# http://localhost:8000/redoc ← ReDoc
```

---

## Configuración del archivo .env

Crear un archivo `.env` en la raíz del proyecto:

```env
# Entorno: development o production
ENVIRONMENT=development
DEBUG=true

# Proveedor activo (cambiar según tu motor)
# Opciones: sqlserver, sqlserverexpress, localdb, postgres, mysql, mariadb
DB_PROVIDER=postgres

# PostgreSQL
DB_POSTGRES=postgresql+asyncpg://usuario:password@localhost:5432/bdfacturas

# SQL Server (formato ODBC)
DB_SQLSERVER=Driver={ODBC Driver 17 for SQL Server};Server=MI_SERVIDOR;Database=bdfacturas;Trusted_Connection=yes;

# MySQL
DB_MYSQL=Server=localhost;Port=3306;Database=bdfacturas;User=root;Password=mi_password;

# MariaDB
DB_MARIADB=Server=localhost;Port=3306;Database=bdfacturas;User=root;Password=;
```

Para cambiar de motor de BD, solo hay que modificar la línea `DB_PROVIDER` y reiniciar la API.

---

## Encriptación de contraseñas (BCrypt)

La tabla `usuario` almacena contraseñas encriptadas con BCrypt (costo 12 por defecto):

```
Texto plano:  "123456"
Hash BCrypt:  "$2b$12$xR3kLz8mN9pQ7vY1wE4aBuOc5dH2gJ6iK8lM0nP3rS5tU7vW9xYz"
```

**Al crear un usuario** (`POST /api/usuario/`):
- El repositorio detecta que `contrasena` es un campo a encriptar
- Aplica BCrypt automáticamente antes del INSERT

**Al verificar credenciales** (`POST /api/usuario/verificar-contrasena`):
- El servicio obtiene el hash almacenado de la BD
- Compara el texto plano contra el hash con `bcrypt.checkpw()`
- Retorna 200 (válida), 401 (incorrecta) o 404 (usuario no existe)

---

## Documentación del tutorial

El proyecto incluye documentación paso a paso en formato `.docx` dentro de la carpeta `docs/`:

| Parte | Documento | Contenido |
|-------|-----------|-----------|
| 1 | Conceptos Fundamentales | FastAPI, async/await, Pydantic, SQLAlchemy |
| 2 | Crear Proyecto y Configuración | Estructura, .env, config.py, pydantic-settings |
| 3 | Capa de Datos | Interfaces, conexión, BCrypt, repositorios (3 motores) |
| 4 | Capa de Negocio | Servicio CRUD, interfaz Protocol, fábrica de repositorios |
| 5 | Modelos y Controllers | Modelos Pydantic (12), controllers específicos (12) |
| 6 | Main (Punto de Entrada) | Registro de routers, orden de prioridad |
| 7 | Repositorios y Servicios Específicos | Refactorización completa: cadena 100% específica por entidad |

---

## Dependencias principales

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `fastapi` | >= 0.100.0 | Framework web async |
| `uvicorn` | >= 0.22.0 | Servidor ASGI |
| `pydantic` | >= 2.0.0 | Validación de datos |
| `pydantic-settings` | >= 2.0.0 | Configuración desde .env |
| `sqlalchemy[asyncio]` | >= 2.0.0 | Query builder async (no ORM) |
| `asyncpg` | >= 0.28.0 | Driver PostgreSQL |
| `aiomysql` | >= 0.2.0 | Driver MySQL / MariaDB |
| `aioodbc` | >= 0.5.0 | Driver SQL Server (ODBC) |
| `bcrypt` | >= 4.0.0 | Encriptación de contraseñas |
| `passlib` | >= 1.7.4 | Utilidades de hashing |

---

## Ventajas y desventajas de la arquitectura

### Ventajas

| # | Ventaja | Explicación |
|---|---------|-------------|
| 1 | **Tipado fuerte y autocompletado** | Cada servicio expone métodos con nombres claros (`obtener_por_codigo`, `obtener_por_email`) en lugar de strings genéricos (`"persona"`, `"codigo"`). El IDE puede autocompletar y detectar errores antes de ejecutar. |
| 2 | **Responsabilidad única** | Cada clase hace una sola cosa. `RepositorioPersonaPostgreSQL` solo sabe de personas en PostgreSQL. No hay una clase gigante que maneje las 12 tablas. |
| 3 | **Cambiar de motor sin tocar lógica** | Para cambiar de PostgreSQL a MySQL solo se modifica `DB_PROVIDER=mysql` en el `.env`. Ni controllers ni servicios se enteran. |
| 4 | **Lógica de negocio por entidad** | `ServicioUsuario` puede encriptar contraseñas, `ServicioFactura` podría validar stock en el futuro. Con un servicio genérico esto sería imposible sin ensuciar el código con `if tabla == "usuario"`. |
| 5 | **Errores en tiempo de desarrollo** | Si alguien escribe `servicio.obtener_por_codgio()` (typo), Python falla inmediatamente. Con el genérico, `servicio.obtener_por_clave("persona", "codgio", valor)` pasaría sin error hasta que llegue el SQL a la BD. |
| 6 | **Interfaces como contratos** | Se puede reemplazar cualquier repositorio por un mock en tests sin tocar nada más. La arquitectura es naturalmente testeable. |
| 7 | **Escalabilidad independiente** | Si la tabla `factura` crece y necesita queries optimizadas, solo se modifica `RepositorioFacturaPostgreSQL` sin riesgo de romper las otras 11 entidades. |

### Desventajas

| # | Desventaja | Explicación |
|---|-----------|-------------|
| 1 | **Código repetitivo (boilerplate)** | 36 repositorios + 12 servicios + 24 interfaces = ~72 archivos casi idénticos. La mayoría solo cambia el nombre de la tabla y la clave primaria. |
| 2 | **Agregar una tabla requiere ~8 archivos** | Modelo Pydantic, interfaz de repositorio, 3 repositorios (uno por motor), interfaz de servicio, servicio, controller, y actualizar la fábrica. Con el genérico bastaba con crear el modelo. |
| 3 | **Las bases siguen siendo genéricas** | Los métodos protegidos `_obtener_filas`, `_crear`, etc. siguen recibiendo `nombre_tabla` como string. El SQL real sigue siendo dinámico. La especificidad es una capa sobre algo genérico internamente. |
| 4 | **La fábrica crece linealmente** | `fabrica_repositorios.py` tiene ~350 líneas con 12 diccionarios y 12 funciones factory casi idénticas. Cada entidad nueva agrega ~20 líneas. |
| 5 | **Riesgo de inconsistencia** | Si se corrige un bug en `RepositorioPersonaPostgreSQL`, hay que recordar aplicar lo mismo en los de SQL Server y MySQL. Con 36 archivos es fácil olvidar uno. |
| 6 | **Sobre-ingeniería para CRUD simple** | Para una API que solo hace SELECT/INSERT/UPDATE/DELETE sin lógica compleja, el servicio genérico era suficiente. La arquitectura específica brilla cuando hay reglas de negocio distintas por entidad. |

### Conclusión

La arquitectura específica es la **correcta a largo plazo** si el proyecto va a crecer con lógica de negocio diferente por entidad (validaciones de factura, permisos por rol, reglas de stock). El costo es el boilerplate inicial. Si el proyecto se queda como CRUD puro, el genérico era más pragmático.

---

## Licencia

Este proyecto es material educativo desarrollado como tutorial de FastAPI con arquitectura en capas y soporte multi-base de datos.
