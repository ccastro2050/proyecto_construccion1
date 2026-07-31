# Especificación — Infraestructura e integración del proyecto

> **Documento 2 de 8** del spec kit **raíz**: cubre lo que une a todo — Docker
> Compose, las 3 bases de datos, el devcontainer y cómo se integran las capas.
>
> | # | Documento | Contenido |
> |---|---|---|
> | 1 | [1_constitution.md](1_constitution.md) | Principios de TODO el proyecto |
> | 2 | **2_spec.md** (este) | QUÉ: los 8 servicios y sus requisitos |
> | 3 | [3_plan.md](3_plan.md) | CÓMO: compose, scripts de BD, devcontainer |
> | 4 | [4_research.md](4_research.md) | Decisiones de infraestructura *(lectura opcional)* |
> | 5 | [5_data_model.md](5_data_model.md) | bdfacturas en los 3 dialectos |
> | 6 | [6_contracts.md](6_contracts.md) | Puertos, variables, healthchecks, montajes |
> | 7 | [7_quickstart.md](7_quickstart.md) | Verificación del sistema completo |
> | 8 | [8_tasks.md](8_tasks.md) | Orden de construcción por fases |
>
> Las aplicaciones (front_flask, api_generica, api_facturas) se tratan aquí
> como **cajas negras**: todo lo que la infraestructura necesita saber de ellas
> (puertos, variables de entorno, comandos, montajes) está en este kit. El
> interior de cada aplicación es un proyecto aparte con su propia
> especificación independiente.

---

## 1. Propósito

Orquestar una arquitectura de 3 capas completa —frontend Flask, dos APIs FastAPI
y tres motores de base de datos con los mismos datos— de forma que un estudiante
la levante con **un solo comando** en cualquier PC con Docker Desktop.

## 2. Componentes a orquestar

| Servicio (compose) | Qué es | Puerto host | Detalle |
|---|---|---|---|
| `front` | Flask (capa 1) | 8000 | build `./front_flask` |
| `api-generica` | FastAPI CRUD genérico (capa 2a) | 8001 | build `./api_generica` |
| `api-facturas` | FastAPI CRUD por entidad (capa 2b) | 8002 | build `./api_facturas` |
| `postgres` | PostgreSQL 16 (alpine) | 15432→5432 | volumen `pgdata` |
| `mariadb` | MariaDB 11 | 13306→3306 | volumen `mariadbdata` |
| `sqlserver` | SQL Server 2022 (Developer) | 11433→1433 | volumen `mssqldata`; ~2 GB RAM |
| `sqlserver-init` | contenedor efímero | — | crea la BD de SQL Server la primera vez y termina |
| `phpmyadmin` | admin web de MariaDB | 8081→80 | auto-login con PMA_USER/PMA_PASSWORD |

## 3. Requisitos funcionales

### RF1 — Arranque con un comando
`docker compose up -d --build` deja los 8 servicios corriendo y las 3 BD **con
datos**. Ningún paso manual adicional.

### RF2 — Base de datos idéntica en 3 motores
Cada motor inicializa la base `bdfacturas` (12 tablas + datos de ejemplo +
trigger de totales/stock + ~15 procedimientos almacenados):
- **PostgreSQL:** `db/postgres/init.sql` montado en `/docker-entrypoint-initdb.d/`
  (se ejecuta solo con volumen vacío).
- **MariaDB:** `db/mariadb/init.sql` ídem (incluye `CREATE DATABASE IF NOT EXISTS`,
  charset utf8mb4).
- **SQL Server:** la imagen no soporta init automático → un servicio auxiliar
  `sqlserver-init` espera el healthcheck de `sqlserver`, verifica con `sqlcmd` si
  la BD existe, y si no, la crea y ejecuta `db/sqlserver/bdfacturas.sql`.

**Esquema (12 tablas):** empresa, persona, producto, rol, ruta, usuario (independientes);
cliente, vendedor, factura, productosporfactura, rol_usuario, rutarol (con FK).
Trigger `actualizar_totales_y_stock` sobre `productosporfactura`: valida stock,
calcula subtotal, ajusta stock y recalcula el total de la factura en INSERT/UPDATE/DELETE.
SP de facturas (insertar/consultar/listar/actualizar/borrar/anular), de usuarios con
roles (crear/actualizar/eliminar/consultar/listar) y de permisos RBAC
(verificar_acceso_ruta, listar/crear/eliminar rutarol), todos retornando JSON.

### RF3 — Selección de motor sin tocar código
Las dos APIs reciben `DB_PROVIDER` (default `postgres` vía `${DB_PROVIDER:-postgres}`)
y las 4 cadenas de conexión (`DB_POSTGRES`, `DB_MARIADB`, `DB_MYSQL`, `DB_SQLSERVER`)
apuntando a los **hosts internos** (`postgres`, `mariadb`, `sqlserver`).
Cambiar motor: `$env:DB_PROVIDER = "mariadb"; docker compose up -d`.

### RF4 — Cableado del front
El front recibe `API_GENERICA_URL=http://api-generica:8001` y
`API_FACTURAS_URL=http://api-facturas:8002` (nombres de servicio, no localhost:
entre contenedores se resuelve por la red interna de compose).

### RF5 — Recarga en caliente
Cada app monta su código como volumen y corre con reload
(`flask --debug` / `uvicorn --reload`). El front además monta el repo completo en
`/workspace` para el devcontainer.

### RF6 — Persistencia
Volúmenes nombrados `pgdata`, `mariadbdata`, `mssqldata`. Los datos sobreviven a
`down` y reinicios; solo `down -v` los borra (y con ello dispara la
re-inicialización en el siguiente `up`).

### RF7 — Healthchecks
- postgres: `pg_isready` cada 5s.
- mariadb: `healthcheck.sh --connect --innodb_initialized` cada 5s.
- sqlserver: `sqlcmd ... SELECT 1` cada 10s, `start_period: 30s` (arranque lento).
- `sqlserver-init` usa `depends_on: condition: service_healthy`.

### RF8 — Administración de BD
- phpMyAdmin en 8081 conectado a `mariadb`, entra directo (PMA_USER/PMA_PASSWORD).
- Devcontainer de VS Code (`.devcontainer/devcontainer.json`): se adosa al servicio
  `front`, workspace `/workspace`, instala Python + Pylance + SQLTools con drivers
  pg/mysql/mssql y **las 3 conexiones preconfiguradas** (hosts internos, puertos estándar).
- Puertos 15432/13306/11433 publicados para herramientas externas del host
  (pgAdmin, HeidiSQL, SSMS).

## 4. Requisitos no funcionales

- **RNF1:** restart `unless-stopped` en front y APIs; `sqlserver-init` con `restart: "no"`.
- **RNF2:** compatible con PCs de estudiantes con poca RAM: todo funciona sin
  SQL Server (que es el único servicio pesado); las demás piezas no dependen de él
  salvo cuando `DB_PROVIDER=sqlserver`.
- **RNF3:** el `docker-compose.yml` lleva un diagrama ASCII de la arquitectura y
  comentarios didácticos en cada servicio.

## 5. Criterios de aceptación

1. En una máquina limpia (solo Docker): `git clone` + `docker compose up -d --build`
   → http://localhost:8000 muestra las dos APIs "en línea".
2. `docker compose ps` muestra front, api-generica, api-facturas, postgres, mariadb,
   sqlserver y phpmyadmin corriendo; `sqlserver-init` con estado Exited (0).
3. Los datos de ejemplo aparecen: 8 productos, 6 personas, 6 facturas.
4. `docker compose down` + `up -d` conserva un registro insertado por el usuario;
   `down -v` + `up -d` lo elimina y restaura los datos originales.
5. Con `DB_PROVIDER=mariadb`, el front sigue funcionando y phpMyAdmin muestra los
   cambios hechos desde el front.
6. pgAdmin/HeidiSQL/SSMS conectan desde el host con los puertos y credenciales de
   la [constitución](1_constitution.md) §6.
7. "Reopen in Container" en VS Code abre el workspace con SQLTools mostrando las
   3 conexiones funcionales.
