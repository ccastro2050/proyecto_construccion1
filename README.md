# Proyecto Paradigmas

Entorno de desarrollo **todo-en-uno con Docker**: programa en Python (API + front) contra **PostgreSQL, MariaDB y SQL Server** al mismo tiempo, y administra las tres bases de datos **desde VS Code**, sin instalar nada más en tu computador.

Base de datos de trabajo: **`bdfacturas`** (facturación con clientes, vendedores, productos, facturas y control de acceso por roles).

---

## Requisitos (solo 3 cosas)

1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) — debe estar **abierto** antes de empezar.
2. [Visual Studio Code](https://code.visualstudio.com/).
3. En VS Code, la extensión **Dev Containers** (`ms-vscode-remote.remote-containers`).

> También necesitas [Git](https://git-scm.com/) para clonar el repositorio.

---

## Puesta en marcha (un solo paso)

```bash
git clone https://github.com/ccastro2050/proyecto_paradigmas.git
```

Abre la carpeta en VS Code. Cuando aparezca la notificación, haz clic en **"Reopen in Container"** (o presiona `F1` → *Dev Containers: Reopen in Container*).

**Eso es todo.** La primera vez tarda unos minutos (descarga las imágenes). Al terminar tendrás:

| Qué | Dónde |
|---|---|
| Frontend de ejemplo | http://localhost:8000 |
| Documentación de la API (Swagger) | http://localhost:8000/docs |
| PostgreSQL 16 con `bdfacturas_postgres_local` | servicio `postgres` (puerto 5432) |
| MariaDB 11 con `bdfacturas_mariadb_local` | servicio `mariadb` (puerto 3306) |
| SQL Server 2022 con `bdfacturas_sqlserver_local` | servicio `sqlserver` (puerto 1433) |

La API arranca sola en una terminal de VS Code (tarea *Iniciar API*). Si la cierras, puedes volver a lanzarla con `F1` → *Tasks: Run Task* → *Iniciar API (FastAPI)*, o manualmente:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Administrar las bases de datos desde VS Code

En la barra lateral izquierda aparece el icono de **SQLTools** (cilindro de base de datos). Las tres conexiones ya están configuradas:

- **PostgreSQL — bdfacturas**
- **MariaDB — bdfacturas**
- **SQL Server — bdfacturas**

Haz clic en una conexión para explorar tablas, ver datos y ejecutar consultas SQL (`Ctrl+E Ctrl+E` ejecuta la consulta seleccionada).

### Credenciales

| Motor | Host (dentro del contenedor) | Puerto en tu PC | Base de datos | Usuario | Contraseña |
|---|---|---|---|---|---|
| PostgreSQL | `postgres` | `15432` | `bdfacturas_postgres_local` | `paradigmas` | `paradigmas123` |
| MariaDB | `mariadb` | `13306` | `bdfacturas_mariadb_local` | `paradigmas` | `paradigmas123` |
| SQL Server | `sqlserver` | `11433` | `bdfacturas_sqlserver_local` | `sa` | `Paradigmas123!` |

> Los puertos de tu PC (`15432`, `13306`, `11433`) son opcionales: sirven si quieres conectarte con herramientas externas (DBeaver, HeidiSQL, SSMS). Desde el código y SQLTools se usa el host interno con el puerto estándar.

---

## Estructura del proyecto

```
proyecto_paradigmas/
├── .devcontainer/        # Configuración del entorno de VS Code (no tocar)
├── .vscode/tasks.json    # Tarea que arranca la API automáticamente
├── docker-compose.yml    # Los 4 contenedores: app + 3 bases de datos
├── db/
│   ├── postgres/init.sql     # Script de la BD para PostgreSQL
│   ├── mariadb/init.sql      # Script de la BD para MariaDB
│   └── sqlserver/            # Script de la BD para SQL Server + inicializador
├── api/                  # ← AQUÍ programas tu API (FastAPI + SQLAlchemy)
│   ├── db.py             # Conexión a los 3 motores
│   └── main.py           # Endpoints de ejemplo (CRUD, JOIN, SQL libre)
├── front/                # ← AQUÍ programas tu frontend (HTML + JS)
│   └── index.html
└── requirements.txt      # Dependencias de Python
```

## La API de ejemplo

El mismo código funciona contra los tres motores — el motor se elige en la URL:

```
GET    /api/salud                        → estado de las 3 conexiones
GET    /api/{motor}/tablas               → lista las tablas
GET    /api/{motor}/productos            → SELECT
POST   /api/{motor}/productos            → INSERT (JSON con codigo, nombre, stock, valorunitario)
PUT    /api/{motor}/productos/{codigo}   → UPDATE
DELETE /api/{motor}/productos/{codigo}   → DELETE
GET    /api/{motor}/facturas             → JOIN de 5 tablas
POST   /api/{motor}/sql                  → ejecuta SQL libre (para prácticas)
```

donde `{motor}` es `postgres`, `mariadb` o `sqlserver`. Ejemplo:

```bash
curl http://localhost:8000/api/postgres/productos
```

---

## Preguntas frecuentes

**¿Cómo apago todo?** Cierra VS Code y ejecuta `docker compose down` en la carpeta del proyecto (o detén los contenedores desde Docker Desktop). Los datos de las bases de datos **se conservan**.

**¿Cómo reinicio las bases de datos a su estado original?** Borra los volúmenes y vuelve a levantar:
```bash
docker compose down -v
docker compose up -d
```

**SQL Server aparece "sin conexión".** Es el contenedor más pesado (~2 GB de RAM) y el más lento en arrancar: espera 1-2 minutos. Si tu equipo tiene poca memoria, puedes trabajar solo con PostgreSQL y MariaDB.

**No aparece "Reopen in Container".** Verifica que Docker Desktop esté abierto y que la extensión *Dev Containers* esté instalada. Luego `F1` → *Dev Containers: Reopen in Container*.

**¿Puedo trabajar sin VS Code?** Sí: `docker compose up -d --build` levanta todo, y la API queda en http://localhost:8000 después de ejecutar dentro del contenedor: `docker compose exec app uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload`.
