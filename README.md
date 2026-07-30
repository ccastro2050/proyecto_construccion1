# Proyecto Paradigmas

Entorno de aprendizaje **todo-en-uno con Docker**: una arquitectura real de **3 capas** — frontend Flask, dos APIs FastAPI y tres motores de base de datos — que se levanta completa con **un solo comando**. Solo se necesita Docker Desktop.

```
Navegador → FRONT Flask (8000)
                ├── API GENÉRICA  (8001)  CRUD sobre cualquier tabla
                └── API FACTURAS  (8002)  CRUD por entidad + validación Pydantic
                        └── PostgreSQL · MariaDB · SQL Server  (bdfacturas)
```

> 📖 **Documentación:** [Guía del estudiante](docs/GUIA_ESTUDIANTE.md) · [Arquitectura de 3 capas](docs/ARQUITECTURA_3_CAPAS.md) · [Principios SOLID y ACID aplicados](docs/PRINCIPIOS_SOLID_ACID.md) · [Conceptos clave](docs/CONCEPTOS.md) · [Cómo se construyó el entorno](docs/TUTORIAL_CONSTRUCCION.md)

---

## Puesta en marcha (un solo comando)

En la terminal de VS Code:

```bash
git clone https://github.com/ccastro2050/proyecto_paradigmas.git
cd proyecto_paradigmas
docker compose up -d --build
```

**Eso es todo.** La primera vez tarda unos minutos (descarga las imágenes). Al terminar:

| Qué | Dónde |
|---|---|
| **Frontend** (Flask + Bootstrap) | http://localhost:8000 |
| **API Genérica** — Swagger | http://localhost:8001/swagger |
| **API Facturas** — Swagger | http://localhost:8002/docs |
| **phpMyAdmin** (admin web de MariaDB) | http://localhost:8081 |
| PostgreSQL 16 · MariaDB 11 · SQL Server 2022 | con la BD `bdfacturas` cargada |

Todo el código está **comentado en español** para quien está comenzando a programar. El código se recarga solo al guardar cambios (front y APIs).

---

## Estructura del proyecto

```
proyecto_paradigmas/
├── docker-compose.yml      # Toda la infraestructura declarada aquí
├── db/                     # Scripts de bdfacturas para los 3 motores
│
├── front_flask/            # CAPA 1 — Frontend (puerto 8000)
│   ├── rutas/              #   Blueprints: productos, personas, facturas, explorador
│   ├── servicios/          #   cliente_api.py: consume cualquiera de las 2 APIs
│   └── templates/          #   HTML con Bootstrap 5 (herencia Jinja2)
│
├── api_generica/           # CAPA 2a — API CRUD genérica (puerto 8001)
│   ├── controllers/        #   /api/{tabla} sirve para CUALQUIER tabla
│   ├── servicios/          #   ServicioCrud + Fábrica + BCrypt
│   └── repositorios/       #   PostgreSQL | MariaDB | SQL Server
│
├── api_facturas/           # CAPA 2b — API por entidad (puerto 8002)
│   ├── controllers/        #   Un controller por tabla (12 entidades)
│   ├── models/             #   Modelos Pydantic (validación estricta)
│   ├── servicios/          #   Lógica de negocio por entidad
│   └── repositorios/       #   Un repositorio por entidad y por motor
│
└── docs/                   # Guías y tutoriales
```

Las dos APIs siguen la misma arquitectura interna de sus repos originales:
[ApiGenericaFastApi_Crud](https://github.com/ccastro2050/ApiGenericaFastApi_Crud) y
[ApiFacturasFastApi_Crud](https://github.com/ccastro2050/ApiFacturasFastApi_Crud).

---

## Cambiar el motor de base de datos

Las dos APIs usan el motor que diga `DB_PROVIDER` (por defecto `postgres`):

```powershell
$env:DB_PROVIDER = "mariadb";   docker compose up -d    # MariaDB
$env:DB_PROVIDER = "sqlserver"; docker compose up -d    # SQL Server
$env:DB_PROVIDER = "postgres";  docker compose up -d    # PostgreSQL (defecto)
```

El front y el resto del sistema no cambian en nada — ese es el punto del curso.

---

## Administrar las bases de datos

- **phpMyAdmin** (MariaDB, sin instalar nada): http://localhost:8081
- **SQLTools en VS Code** (los 3 motores): `F1` → *Dev Containers: Reopen in Container* → icono del cilindro
- **Herramientas locales**: pgAdmin (`localhost:15432`), HeidiSQL (`localhost:13306`), SSMS (`localhost,11433`)

| Motor | Base de datos | Usuario | Contraseña | Puerto en su PC |
|---|---|---|---|---|
| PostgreSQL | `bdfacturas_postgres_local` | `paradigmas` | `paradigmas123` | `15432` |
| MariaDB | `bdfacturas_mariadb_local` | `paradigmas` | `paradigmas123` | `13306` |
| SQL Server | `bdfacturas_sqlserver_local` | `sa` | `Paradigmas123!` | `11433` |

---

## Comandos útiles

```bash
docker compose down          # apagar todo (los datos se conservan)
docker compose up -d         # volver a encender (segundos)
docker compose down -v       # resetear las BD a su estado original
docker compose ps            # estado de los contenedores
docker compose logs front    # errores del front (o api-generica / api-facturas)
```

---

*Proyecto Paradigmas · USB Med · Base de datos bdfacturas (facturación + RBAC con triggers y stored procedures)*
