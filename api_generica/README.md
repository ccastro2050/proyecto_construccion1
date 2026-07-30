# ApiGenericaFastApi_Crud - API REST Generica CRUD Multi-Base de Datos

```bash
git clone https://github.com/ccastro2050/ApiGenericaFastApi_Crud.git
git clone https://github.com/ccastro2050/FrontFlaskTutorial.git
```

![Python Version](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![Database](https://img.shields.io/badge/DB-SQL_Server_%7C_Postgres_%7C_MySQL-brightgreen?logo=databricks)
![Architecture](https://img.shields.io/badge/Architecture-Clean_%26_SOLID-orange)
![License](https://img.shields.io/badge/License-Educativo-lightgrey)

API REST generica para operaciones CRUD sobre cualquier tabla de base de datos. Soporta multiples motores con una sola configuracion.

---

## Caracteristicas

- **CRUD Generico**: Operaciones Create, Read, Update, Delete sobre cualquier tabla
- **Multi-Base de Datos**: SQL Server, SQL Server Express, LocalDB, PostgreSQL, MySQL, MariaDB
- **Swagger UI**: Documentacion interactiva automatica
- **Encriptacion BCrypt**: Hash seguro de contrasenas
- **CORS Configurado**: Listo para consumir desde frontend
- **Async/Await**: Operaciones asincronas para mejor rendimiento
- **Arquitectura Limpia**: Separacion en 3 capas (Controller -> Servicio -> Repositorio)
- **Principios SOLID**: Diseno extensible y mantenible

---

## Arquitectura

```
+----------------------------------------------+
|        CONTROLLERS (Presentacion)            |
|           entidades_controller               |
+----------------------+-----------------------+
                       |
                       v
+----------------------------------------------+
|          SERVICIOS (Negocio)                 |
|    ServicioCrud + FabricaRepositorios        |
+----------------------+-----------------------+
                       |
                       v
+----------------------------------------------+
|         REPOSITORIOS (Datos)                 |
|  SQL Server | PostgreSQL | MySQL/MariaDB     |
|  (aioodbc)  | (asyncpg)  | (aiomysql)       |
+----------------------+-----------------------+
                       |
                       v
+----------------------------------------------+
|            BASE DE DATOS                     |
+----------------------------------------------+
```

---

## Requisitos

| Requisito | Version |
|-----------|---------|
| Python | 3.11 o superior |
| pip | Ultima version |
| Git | Ultima version |
| Visual Studio Code | Ultima version (recomendado) |
| Base de datos | SQL Server, PostgreSQL, MySQL o MariaDB |

---

## Instalacion

### 1. Clonar el repositorio

```bash
git clone https://github.com/ccastro2050/ApiGenericaFastApi_Crud.git
cd ApiGenericaFastApi_Crud
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\activate

# Windows (Git Bash)
source venv/Scripts/activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear un archivo `.env` en la raiz (ver seccion Configuracion).

### 5. Ejecutar la API

```bash
# Desarrollo (con auto-reload)
uvicorn main:app --reload --port 8000

# O directamente
python main.py
```

### 6. Abrir documentacion

| Documentacion | URL |
|---------------|-----|
| Swagger UI | http://localhost:8000/swagger |
| ReDoc | http://localhost:8000/redoc |
| OpenAPI JSON | http://localhost:8000/swagger/v1/swagger.json |

---

## Configuracion

### Archivo .env

```env
ENVIRONMENT=production
DEBUG=false

# Proveedor activo
DB_PROVIDER=postgres

# Cadenas de conexion
DB_SQLSERVER=Driver={ODBC Driver 17 for SQL Server};Server=MI_SERVIDOR;Database=mi_bd;Trusted_Connection=yes;TrustServerCertificate=yes;
DB_SQLSERVEREXPRESS=Driver={ODBC Driver 17 for SQL Server};Server=MI_SERVIDOR\SQLEXPRESS;Database=mi_bd;Trusted_Connection=yes;TrustServerCertificate=yes;
DB_LOCALDB=Driver={ODBC Driver 17 for SQL Server};Server=(localdb)\MSSQLLocalDB;Database=mi_bd;Trusted_Connection=yes;TrustServerCertificate=yes;
DB_POSTGRES=postgresql+asyncpg://usuario:password@localhost:5432/mi_bd
DB_MYSQL=Server=localhost;Port=3306;Database=mi_bd;User=root;Password=mi_password;CharSet=utf8mb4;
DB_MARIADB=Server=localhost;Port=3306;Database=mi_bd;User=root;Password=;
```

### Cambiar de base de datos

Solo modificar `DB_PROVIDER`:

| Valor | Base de datos |
|-------|---------------|
| `sqlserver` | Microsoft SQL Server |
| `sqlserverexpress` | SQL Server Express |
| `localdb` | SQL Server LocalDB (desarrollo) |
| `postgres` | PostgreSQL |
| `mysql` | MySQL |
| `mariadb` | MariaDB |

---

## Bases de Datos Soportadas

| Base de Datos | Driver Python | Puerto Default |
|---------------|---------------|----------------|
| SQL Server | aioodbc | 1433 |
| SQL Server Express | aioodbc | 1433 |
| SQL Server LocalDB | aioodbc | - |
| PostgreSQL | asyncpg | 5432 |
| MySQL | aiomysql | 3306 |
| MariaDB | aiomysql | 3306 |

---

## Endpoints

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/{tabla}` | Listar registros |
| GET | `/api/{tabla}/{clave}/{valor}` | Filtrar por clave |
| POST | `/api/{tabla}` | Crear registro |
| PUT | `/api/{tabla}/{clave}/{valor}` | Actualizar registro |
| DELETE | `/api/{tabla}/{clave}/{valor}` | Eliminar registro |
| POST | `/api/{tabla}/verificar-contrasena` | Verificar credenciales BCrypt |

**Parametros opcionales (query string):**

| Parametro | Endpoints | Descripcion |
|-----------|-----------|-------------|
| `esquema` | Todos | Esquema de la BD (default: `public`/`dbo`) |
| `limite` | GET listar | Maximo de registros (default: 1000) |
| `campos_encriptar` | POST, PUT | Campos a hashear con BCrypt |

---

## Ejemplos de Uso

### Listar productos

```http
GET /api/producto?limite=50
```

### Buscar por clave

```http
GET /api/producto/codigo/PR004
```

### Crear registro

```http
POST /api/producto
Content-Type: application/json

{
    "codigo": "PR999",
    "nombre": "Laptop HP",
    "stock": 25,
    "valorunitario": 1500000
}
```

### Actualizar registro

```http
PUT /api/producto/codigo/PR999
Content-Type: application/json

{
    "nombre": "Laptop HP Actualizada",
    "stock": 30
}
```

### Eliminar registro

```http
DELETE /api/producto/codigo/PR999
```

### Crear usuario con contrasena encriptada

```http
POST /api/usuario?campos_encriptar=contrasena
Content-Type: application/json

{
    "email": "test@test.com",
    "contrasena": "123456",
    "nombre": "Test"
}
```

### Verificar contrasena

```http
POST /api/usuario/verificar-contrasena?campo_usuario=email&campo_contrasena=contrasena&valor_usuario=test@test.com&valor_contrasena=123456
```

---

## Estructura del Proyecto

```
ApiGenericaFastApi_Crud/
|-- main.py                                    <- Punto de entrada
|-- config.py                                  <- Configuracion desde .env
|-- requirements.txt                           <- Dependencias
|-- .env                                       <- Variables de entorno
|-- .gitignore
|
|-- .vscode/
|   |-- launch.json                            <- Debug con F5
|   +-- settings.json                          <- Interprete Python
|
|-- controllers/
|   |-- __init__.py
|   +-- entidades_controller.py                <- 6 endpoints CRUD
|
|-- servicios/
|   |-- __init__.py
|   |-- servicio_crud.py                       <- Logica de negocio
|   |-- fabrica_repositorios.py                <- Factory pattern
|   |-- abstracciones/
|   |   |-- __init__.py
|   |   |-- i_servicio_crud.py                 <- Protocol del servicio
|   |   +-- i_proveedor_conexion.py            <- Protocol de conexion
|   |-- conexion/
|   |   |-- __init__.py
|   |   +-- proveedor_conexion.py              <- Lee cadenas desde .env
|   +-- utilidades/
|       |-- __init__.py
|       +-- encriptacion_bcrypt.py             <- Hash y verificacion BCrypt
|
|-- repositorios/
|   |-- __init__.py
|   |-- abstracciones/
|   |   |-- __init__.py
|   |   +-- i_repositorio_lectura_tabla.py     <- Protocol del repositorio
|   |-- repositorio_lectura_postgresql.py       <- PostgreSQL
|   |-- repositorio_lectura_sqlserver.py        <- SQL Server
|   +-- repositorio_lectura_mysql_mariadb.py    <- MySQL/MariaDB
|
+-- script_bd/
    |-- bdfacturas_postgres.sql                <- Script PostgreSQL
    |-- bdfacturas_sqlserver.sql               <- Script SQL Server
    +-- bdfacturas_mysql_mariadb.sql           <- Script MySQL/MariaDB
```

---

## Descripcion de Clases y Conceptos Arquitectonicos

### Punto de Entrada

| Archivo | Descripcion | Concepto |
|---------|-------------|----------|
| `main.py` | Crea la aplicacion FastAPI, configura CORS, registra el router del controlador y arranca el servidor Uvicorn. Es el unico archivo que se ejecuta directamente. | **Composition Root** — Punto donde se ensamblan todas las piezas de la aplicacion. Aqui se conecta el framework (FastAPI) con los componentes internos sin que estos conozcan al framework. |

### Configuracion

| Clase / Archivo | Descripcion | Concepto |
|-----------------|-------------|----------|
| `Settings` (`config.py`) | Clase que agrupa toda la configuracion de la aplicacion (debug, entorno, base de datos). Usa `pydantic-settings` para leer variables desde archivos `.env` con validacion automatica de tipos. | **Centralized Configuration** — La configuracion vive en un solo lugar y se inyecta donde se necesite, en vez de leer variables de entorno dispersas por el codigo. |
| `DatabaseSettings` (`config.py`) | Subclase de configuracion que contiene las cadenas de conexion de todos los proveedores de BD. Lee variables con prefijo `DB_` del `.env`. | **Configuration Section** — Agrupa configuraciones relacionadas bajo un mismo objeto, facilitando el acceso (ej: `settings.database.postgres`). |
| `get_settings()` (`config.py`) | Funcion decorada con `@lru_cache` que retorna siempre la misma instancia de `Settings`. | **Singleton Pattern** — Garantiza una unica instancia de configuracion en toda la aplicacion, evitando lecturas repetidas del `.env`. |

### Capa de Presentacion (Controllers)

| Clase / Archivo | Descripcion | Concepto |
|-----------------|-------------|----------|
| `entidades_controller.py` | Router de FastAPI que expone 6 endpoints HTTP (GET listar, GET por clave, POST crear, PUT actualizar, DELETE eliminar, POST verificar contrasena). Recibe peticiones, valida parametros basicos, delega al servicio y retorna respuestas JSON con codigos HTTP apropiados. | **Controller / Presentation Layer** — Capa mas externa de la arquitectura. Su unica responsabilidad es traducir peticiones HTTP a llamadas de servicio y formatear las respuestas. No contiene logica de negocio ni acceso a datos. |

### Capa de Negocio (Servicios)

| Clase / Archivo | Descripcion | Concepto |
|-----------------|-------------|----------|
| `ServicioCrud` (`servicio_crud.py`) | Coordina las operaciones CRUD aplicando reglas de negocio: valida que nombres de tabla, claves y valores no esten vacios, normaliza esquemas, y delega la ejecucion al repositorio. Para verificar contrasenas, obtiene el hash almacenado y lo compara con BCrypt. | **Service Layer / Business Logic** — Capa intermedia que contiene las reglas del dominio. Recibe un repositorio por constructor (inyeccion de dependencias) y trabaja con la abstraccion `IRepositorioLecturaTabla`, sin conocer que base de datos se usa. |
| `crear_servicio_crud()` (`fabrica_repositorios.py`) | Funcion que lee `DB_PROVIDER` del `.env`, busca la clase de repositorio correspondiente en un diccionario y crea el `ServicioCrud` con ese repositorio ya instanciado. | **Factory Pattern** — Encapsula la logica de creacion de objetos. El controlador llama a `crear_servicio_crud()` sin saber que repositorio concreto se crea. Agregar un nuevo proveedor de BD = agregar 1 linea al diccionario. |

### Abstracciones (Interfaces / Protocols)

| Clase / Archivo | Descripcion | Concepto |
|-----------------|-------------|----------|
| `IRepositorioLecturaTabla` (`repositorios/abstracciones/`) | Protocol que define 6 metodos que todo repositorio debe implementar: `obtener_filas`, `obtener_por_clave`, `crear`, `actualizar`, `eliminar` y `obtener_hash_contrasena`. | **Interface / Contract (Repository Pattern)** — Define QUE operaciones puede hacer un repositorio, sin definir COMO. Cada proveedor (PostgreSQL, SQL Server, MySQL) implementa estos metodos a su manera. Permite cambiar de base de datos sin modificar el servicio. |
| `IServicioCrud` (`servicios/abstracciones/`) | Protocol que define los 6 metodos del servicio CRUD: `listar`, `obtener_por_clave`, `crear`, `actualizar`, `eliminar` y `verificar_contrasena`. | **Interface / Contract (Service Pattern)** — Contrato de la capa de negocio. Permite que el controlador dependa de una abstraccion en vez de la implementacion concreta. Facilita pruebas unitarias con mocks. |
| `IProveedorConexion` (`servicios/abstracciones/`) | Protocol con 2 miembros: propiedad `proveedor_actual` (nombre del proveedor) y metodo `obtener_cadena_conexion()` (cadena de conexion activa). | **Interface / Contract (Strategy Pattern)** — Abstrae la fuente de las cadenas de conexion. Los repositorios reciben un `IProveedorConexion` sin saber si viene de un `.env`, una variable de entorno o un servicio externo. |

### Conexion

| Clase / Archivo | Descripcion | Concepto |
|-----------------|-------------|----------|
| `ProveedorConexion` (`servicios/conexion/`) | Implementacion concreta de `IProveedorConexion`. Lee `DB_PROVIDER` y las cadenas de conexion desde `Settings`. Contiene un diccionario que mapea nombre de proveedor a su cadena correspondiente. | **Concrete Strategy** — Implementacion concreta del contrato `IProveedorConexion`. Centraliza la logica de seleccion de cadena de conexion en un solo lugar, evitando `if/else` dispersos. |

### Capa de Datos (Repositorios)

| Clase / Archivo | Descripcion | Concepto |
|-----------------|-------------|----------|
| `RepositorioLecturaPostgreSQL` (`repositorios/`) | Implementa las 6 operaciones CRUD para PostgreSQL. Usa identificadores con `"comillas dobles"`, `LIMIT` para paginacion, esquema por defecto `public`, y `SQLAlchemy async` con driver `asyncpg`. Convierte tipos (Decimal, datetime, UUID) a formatos serializables JSON. | **Repository Pattern (Concrete Implementation)** — Encapsula todo el acceso a datos especifico de PostgreSQL. La capa de negocio no sabe que existe PostgreSQL; solo llama metodos del contrato `IRepositorioLecturaTabla`. |
| `RepositorioLecturaSqlServer` (`repositorios/`) | Implementa las 6 operaciones CRUD para SQL Server. Usa identificadores con `[corchetes]`, `TOP(n)` en lugar de `LIMIT`, esquema por defecto `dbo`. Convierte cadenas ODBC a URL de SQLAlchemy (`mssql+aioodbc`). Detecta tipos de columna via `INFORMATION_SCHEMA` para convertir valores correctamente. | **Repository Pattern (Concrete Implementation)** — Misma interfaz, distinta implementacion. Encapsula las particularidades de SQL Server (sintaxis T-SQL, driver ODBC, formato de cadenas de conexion) detras del contrato comun. |
| `RepositorioLecturaMysqlMariaDB` (`repositorios/`) | Implementa las 6 operaciones CRUD para MySQL y MariaDB. Usa identificadores con `` `backticks` ``, `LIMIT` con parametro, sin esquema tradicional (la BD es el contenedor). Convierte cadenas formato C# (`Server=...;Port=...`) a URL de SQLAlchemy (`mysql+aiomysql`). Maneja tipos adicionales como `timedelta` y `bytes`. | **Repository Pattern (Concrete Implementation)** — Un solo repositorio sirve para MySQL y MariaDB porque comparten sintaxis SQL y driver. Demuestra reutilizacion cuando dos proveedores son compatibles. |

### Utilidades

| Clase / Archivo | Descripcion | Concepto |
|-----------------|-------------|----------|
| `encriptar()` (`servicios/utilidades/encriptacion_bcrypt.py`) | Genera un hash BCrypt de 60 caracteres a partir de un texto plano. Configurable con costo (default 12, rango 4-31). | **Utility / Helper** — Funcion pura sin estado ni dependencias externas. Se usa en los repositorios al crear/actualizar registros con campos encriptados. |
| `verificar()` (`servicios/utilidades/encriptacion_bcrypt.py`) | Compara un texto plano contra un hash BCrypt existente. Retorna `True` si coinciden, `False` en caso contrario. | **Utility / Helper** — Complemento de `encriptar()`. Se usa en `ServicioCrud.verificar_contrasena()` para validar credenciales sin exponer el hash. |

### Scripts de Base de Datos

| Archivo | Descripcion | Contenido |
|---------|-------------|-----------|
| `bdfacturas_postgres.sql` | Script DDL + DML para PostgreSQL 10+. | Tablas, constraints, datos de ejemplo, trigger `plpgsql` (INSERT/UPDATE/DELETE en un solo trigger) y 5 stored procedures con parametros `INOUT` tipo JSON. |
| `bdfacturas_sqlserver.sql` | Script DDL + DML para SQL Server 2016+. | Tablas, constraints, datos de ejemplo, 3 triggers separados (INSERT, UPDATE, DELETE) y 5 stored procedures con `FOR JSON`. |
| `bdfacturas_mysql_mariadb.sql` | Script DDL + DML para MySQL 8+ / MariaDB 10.5+. | Tablas `InnoDB` con `utf8mb4`, constraints, datos de ejemplo, 3 triggers separados con `SIGNAL SQLSTATE`, y 5 stored procedures con `JSON_OBJECT` / `JSON_ARRAYAGG`. |

### Flujo de una Peticion

```
1. Cliente HTTP (Swagger, Postman, Frontend)
        |
        v
2. entidades_controller.py          <- Recibe HTTP, valida parametros
        |
        v
3. fabrica_repositorios.py           <- Lee DB_PROVIDER, crea repositorio + servicio
        |
        v
4. ServicioCrud                      <- Aplica reglas de negocio, delega al repositorio
        |
        v
5. RepositorioLectura[Proveedor]     <- Ejecuta SQL especifico del motor
        |
        v
6. Base de Datos                     <- Triggers se ejecutan automaticamente
        |
        v
7. Respuesta JSON al cliente
```

---

## Principios SOLID Aplicados

| Principio | Aplicacion |
|-----------|------------|
| **S** - Single Responsibility | Controller, Servicio y Repositorio separados |
| **O** - Open/Closed | Nueva BD = nueva clase + 1 linea en fabrica |
| **L** - Liskov Substitution | Cambiar `DB_PROVIDER` en `.env`, todo sigue funcionando |
| **I** - Interface Segregation | Protocols pequenos y especificos |
| **D** - Dependency Inversion | Servicios reciben abstracciones, no clases concretas |

---

## Tecnologias Utilizadas

| Tecnologia | Version | Proposito |
|------------|---------|-----------|
| Python | 3.11+ | Lenguaje principal |
| FastAPI | 0.100+ | Framework web async |
| Uvicorn | 0.22+ | Servidor ASGI |
| Pydantic | 2.0+ | Validacion de datos |
| pydantic-settings | 2.0+ | Configuracion desde .env |
| passlib + bcrypt | 1.7+ | Hash de contrasenas |
| SQLAlchemy | 2.0+ | Engine async para queries |
| asyncpg | 0.28+ | Driver PostgreSQL |
| aiomysql | 0.2+ | Driver MySQL/MariaDB |
| aioodbc | 0.5+ | Driver SQL Server |

---

## Solucion de Problemas Comunes

### Error de conexion a la base de datos

**Sintoma**: `Connection refused` o `timeout`

**Solucion**:
- Verificar que el servicio de la BD este corriendo
- Revisar que `DB_PROVIDER` coincida con una cadena configurada
- Para SQL Server, asegurar tener ODBC Driver 17 instalado

### ModuleNotFoundError

**Sintoma**: `No module named 'fastapi'`

**Solucion**:
```bash
# Verificar que el entorno virtual este activo
.\venv\Scripts\activate

# Reinstalar dependencias
pip install -r requirements.txt
```

### Pylance no resuelve imports

**Sintoma**: `Import "fastapi" could not be resolved`

**Solucion**: `Ctrl+Shift+P` -> `Python: Select Interpreter` -> seleccionar `.\venv\Scripts\python.exe`

### Puerto en uso

**Sintoma**: `Address already in use`

**Solucion**:
```bash
# Cambiar puerto
uvicorn main:app --reload --port 8001
```

---

## Comandos Utiles

```bash
# Activar entorno virtual
.\venv\Scripts\activate              # Windows PowerShell
source venv/Scripts/activate         # Windows Git Bash
source venv/bin/activate             # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar en desarrollo
uvicorn main:app --reload --port 8000

# Ejecutar en produccion
uvicorn main:app --host 0.0.0.0 --port 8000

# Debug en VS Code
F5
```

---

## Licencia

Este proyecto es de uso educativo.

---

## Autor

Basado en el proyecto ApiGenericaCsharp de Carlos Arturo Castro Castro.

Version simplificada en Python/FastAPI enfocada en CRUD generico.
