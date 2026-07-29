# Conceptos clave — Proyecto Paradigmas

Resumen de los conceptos que usa este proyecto. Cada uno en pocas líneas.

---

## 1. Contenedores y Docker

**Docker** empaqueta un programa con todo lo que necesita (sistema, librerías, configuración) en una unidad llamada **contenedor**, que corre igual en cualquier máquina.

- **Imagen:** la "plantilla" (ej. `postgres:16`, `python:3.12`). Se descarga una vez.
- **Contenedor:** una imagen en ejecución. Se puede crear, apagar y borrar sin afectar su PC.
- **Volumen:** disco persistente del contenedor. Por eso los datos de las BD **sobreviven** al apagar; solo se borran con `docker compose down -v`.
- **Ventaja en este curso:** nadie instala PostgreSQL, MariaDB, SQL Server ni Python — todos tienen exactamente el mismo entorno.

## 2. Docker Compose

Herramienta que levanta **varios contenedores a la vez** definidos en el archivo `docker-compose.yml`. En este proyecto son 4 servicios:

| Servicio | Qué es |
|---|---|
| `app` | Contenedor de desarrollo: Python + su código |
| `postgres` | PostgreSQL 16 con la BD cargada |
| `mariadb` | MariaDB 11 con la BD cargada |
| `sqlserver` (+ `sqlserver-init`) | SQL Server 2022; el "init" crea la BD la primera vez |

Los servicios se comunican por una red interna usando su **nombre como host** (ej. desde Python se conecta a `postgres`, no a `localhost`).

## 3. Dev Containers (VS Code)

Extensión que hace que VS Code trabaje **dentro** del contenedor `app`: el editor, la terminal y el depurador ven el Python y las librerías del contenedor, no las de su PC. La configuración está en `.devcontainer/devcontainer.json` (qué servicio usar, qué extensiones instalar, qué conexiones de BD dejar listas). Por eso el entorno queda igual para todos con un solo clic.

## 4. Sistemas de gestión de bases de datos (SGBD)

Los tres motores del proyecto son **relacionales** (tablas, filas, claves, SQL), pero cada uno es un producto distinto con dialecto propio:

| Motor | Origen | Detalles de dialecto (ejemplos) |
|---|---|---|
| **PostgreSQL** | Código abierto | `SERIAL` para autoincrementos, `LIMIT n` |
| **MariaDB** | Código abierto (derivado de MySQL) | `AUTO_INCREMENT`, `LIMIT n`, motor InnoDB |
| **SQL Server** | Microsoft | `IDENTITY`, `TOP n`, tipos `NVARCHAR` |

**Idea central del curso:** el SQL estándar (SELECT, JOIN, INSERT…) funciona igual en los tres; las diferencias aparecen en autoincrementos, paginación, funciones y procedimientos almacenados.

## 5. La base de datos `bdfacturas`

Modelo de facturación con control de acceso:

- **Negocio:** `empresa`, `persona`, `cliente`, `vendedor`, `producto`, `factura`, `productosporfactura` (detalle de la factura).
- **Seguridad (RBAC):** `usuario`, `rol`, `rol_usuario`, `ruta`, `rutarol` — qué rol puede entrar a qué ruta de la aplicación.
- **Triggers:** al insertar/modificar/borrar el detalle de una factura, la BD **automáticamente** valida stock, calcula subtotales y actualiza el total.
- **Procedimientos almacenados** (MariaDB y SQL Server): operaciones completas empaquetadas en la BD (ej. crear factura con sus productos en una sola llamada).

## 6. API REST

Una **API** expone operaciones por HTTP para que cualquier cliente (el frontend, `curl`, otra app) las use. Estilo **REST**: las URL representan recursos y los verbos HTTP la acción:

| Verbo | Acción | Ejemplo en este proyecto |
|---|---|---|
| GET | Consultar | `GET /api/postgres/productos` |
| POST | Crear | `POST /api/mariadb/productos` |
| PUT | Actualizar | `PUT /api/sqlserver/productos/PR001` |
| DELETE | Borrar | `DELETE /api/postgres/productos/PR001` |

Los datos viajan en formato **JSON**.

## 7. FastAPI

Framework de Python para construir APIs. Cada función con un decorador (`@app.get(...)`) se vuelve un endpoint. Genera **documentación automática** en `/docs` (Swagger), donde se puede probar la API sin escribir código. Con `--reload`, la API se reinicia sola al guardar cambios.

## 8. SQLAlchemy y la conexión a las BD

Librería de Python para hablar con bases de datos. Aquí se usa con **SQL directo** (`text(...)`) y un **engine por motor**; la URL de conexión indica dialecto y driver:

```
postgresql+psycopg2://usuario:clave@host:puerto/base
mysql+pymysql://...
mssql+pymssql://...
```

Gracias a esto, **el mismo código Python** funciona contra los tres motores cambiando solo la URL — esa es la comparación de paradigmas del proyecto.

**Consultas parametrizadas:** los valores se pasan como parámetros (`:codigo`) y no concatenados en el string. Evita la **inyección SQL**, el ataque más común contra aplicaciones con BD.

## 9. Frontend

Página HTML + JavaScript (carpeta `front/`) servida por la misma API. Usa `fetch()` para llamar los endpoints y pinta los resultados. No requiere framework: es la base para entender cómo un cliente consume una API REST.

## 10. Arquitectura completa del proyecto

```
Navegador (front/index.html)
        │  HTTP + JSON
        ▼
API FastAPI (api/main.py)  ← usted programa aquí
        │  SQLAlchemy (SQL parametrizado)
        ▼
┌────────────┬────────────┬────────────┐
│ PostgreSQL │  MariaDB   │ SQL Server │   ← contenedores Docker
│ bdfacturas │ bdfacturas │ bdfacturas │
└────────────┴────────────┴────────────┘
```
