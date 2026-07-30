# Contratos de integración — Proyecto Paradigmas

> **Documento 6 de 8** del spec kit raíz: cómo se hablan las piezas entre sí
> (puertos, hosts, variables, healthchecks). Los contratos HTTP detallados de
> cada API viven en su propio kit
> (`api_generica/docs/spec_kit/6_contracts.md` · `api_facturas/docs/spec_kit/6_contracts.md`).

---

## 1. Mapa de puertos

| Servicio | Host interno (red compose) | Puerto publicado al PC |
|---|---|---|
| front | `front:8000` | **8000** |
| api-generica | `api-generica:8001` | **8001** (`/swagger`) |
| api-facturas | `api-facturas:8002` | **8002** (`/docs`) |
| postgres | `postgres:5432` | **15432** |
| mariadb | `mariadb:3306` | **13306** |
| sqlserver | `sqlserver:1433` | **11433** |
| phpmyadmin | `phpmyadmin:80` | **8081** |

Regla: **entre contenedores** siempre el host interno con puerto estándar;
**desde el PC** siempre localhost con el puerto publicado.

## 2. Variables de entorno (el contrato de configuración)

### front
| Variable | Valor en compose |
|---|---|
| `API_GENERICA_URL` | `http://api-generica:8001` |
| `API_FACTURAS_URL` | `http://api-facturas:8002` |

### api-generica y api-facturas (idénticas)
| Variable | Valor |
|---|---|
| `DB_PROVIDER` | `${DB_PROVIDER:-postgres}` — la variable del shell del host decide; default postgres |
| `DB_POSTGRES` | `postgresql+asyncpg://paradigmas:paradigmas123@postgres:5432/bdfacturas_postgres_local` |
| `DB_MARIADB` / `DB_MYSQL` | `mysql+aiomysql://paradigmas:paradigmas123@mariadb:3306/bdfacturas_mariadb_local` |
| `DB_SQLSERVER` | `mssql+aioodbc://sa:Paradigmas123!@sqlserver:1433/bdfacturas_sqlserver_local?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes` |

### Motores
postgres: `POSTGRES_DB/USER/PASSWORD` · mariadb: `MARIADB_ROOT_PASSWORD/DATABASE/USER/PASSWORD` ·
sqlserver: `ACCEPT_EULA=Y`, `MSSQL_SA_PASSWORD`, `MSSQL_PID=Developer` ·
phpmyadmin: `PMA_HOST=mariadb`, `PMA_USER/PMA_PASSWORD` (auto-login).

## 3. Contrato front ↔ APIs (resumen)

- Healthcheck de "en línea": `GET {api}/` responde JSON (5 s de timeout).
- CRUD: sobre `{tabla, total, datos}`; API Genérica usa
  `/api/{tabla}[/{clave}/{valor}]`, API Facturas usa `/api/{tabla}/[{valor}]`
  (colecciones con barra final). Errores FastAPI: `{"detail": {estado, mensaje, detalle}}`.
- El front consume del **lado servidor** (por eso las APIs funcionan sin CORS).

## 4. Contrato APIs ↔ BD

- La BD activa la decide `DB_PROVIDER`; las 3 conviven levantadas.
- Los engines se crean de forma **perezosa** (primera petición) → las APIs
  arrancan aunque las BD aún estén inicializando; no hay `depends_on` apps→BD.
- La lógica de facturación (trigger + SP) es de la BD: las APIs insertan crudo
  y los errores del trigger viajan como 500 con el mensaje del motor.

## 5. Healthchecks y arranque

| Servicio | Check | Parámetros |
|---|---|---|
| postgres | `pg_isready -U paradigmas -d bdfacturas_postgres_local` | cada 5 s, 10 reintentos |
| mariadb | `healthcheck.sh --connect --innodb_initialized` | cada 5 s, 10 reintentos |
| sqlserver | `sqlcmd -C -Q 'SELECT 1'` | cada 10 s, 20 reintentos, `start_period` 30 s |
| sqlserver-init | `depends_on: sqlserver: condition: service_healthy`; termina Exited (0) | `restart: "no"` |

## 6. Contratos de volúmenes y montajes

| Montaje | Para qué |
|---|---|
| `pgdata`, `mariadbdata`, `mssqldata` (nombrados) | Persistencia de datos; `down -v` = reset |
| `./db/postgres/init.sql → /docker-entrypoint-initdb.d/` (ro) | Init de PostgreSQL (solo volumen vacío) |
| `./db/mariadb/init.sql → /docker-entrypoint-initdb.d/` (ro) | Init de MariaDB |
| `./db/sqlserver → /scripts` (ro, en sqlserver-init) | `init.sh` + `bdfacturas.sql` |
| `./front_flask → /app`, `./api_* → /app` | Recarga en caliente |
| `. → /workspace:cached` (solo front) | Devcontainer de VS Code |

## 7. Devcontainer (contrato con VS Code)

`.devcontainer/devcontainer.json`: `service: front`, `workspaceFolder: /workspace`,
`forwardPorts: [8000, 8001, 8002]`, extensiones Python + Pylance + SQLTools
(drivers pg/mysql/mssql) y 3 conexiones SQLTools con **hosts internos**
(`postgres:5432`, `mariadb:3306`, `sqlserver:1433` con
`encrypt + trustServerCertificate`).

## 8. Credenciales (fijas en todo el proyecto)

| Motor | BD | Usuario | Clave |
|---|---|---|---|
| PostgreSQL | `bdfacturas_postgres_local` | `paradigmas` | `paradigmas123` |
| MariaDB | `bdfacturas_mariadb_local` | `paradigmas` | `paradigmas123` |
| SQL Server | `bdfacturas_sqlserver_local` | `sa` | `Paradigmas123!` |
