# Plan técnico — Infraestructura e integración

> **Documento 3 de 8** del spec kit raíz: **CÓMO** montar lo especificado en
> [2_spec.md](2_spec.md), bajo los principios de [1_constitution.md](1_constitution.md).
> El porqué de cada decisión: [4_research.md](4_research.md) · orden de trabajo:
> [8_tasks.md](8_tasks.md).

---

## 1. Estructura de archivos en la raíz del repositorio

```
proyecto_construccion1/
├── docker-compose.yml          # los 8 servicios + 3 volúmenes
├── README.md
├── .gitignore / .gitattributes
├── .devcontainer/
│   └── devcontainer.json       # VS Code adosado al servicio front
├── .vscode/                    # ajustes locales del editor
├── db/
│   ├── postgres/init.sql       # esquema + datos + trigger + SPs (dialecto PostgreSQL)
│   ├── mariadb/init.sql        # ídem en dialecto MySQL/MariaDB (~1300 líneas)
│   └── sqlserver/
│       ├── bdfacturas.sql      # ídem en dialecto T-SQL (~1480 líneas)
│       └── init.sh             # crea la BD y ejecuta el .sql solo la primera vez
├── docs/                       # documentación general + este spec kit
├── front_flask/                # capa 1 — frontend Flask (puerto 8000)
├── api_generica/               # capa 2a — API CRUD genérica (puerto 8001)
└── api_facturas/               # capa 2b — API por entidad (puerto 8002)
```

## 2. docker-compose.yml — decisiones por servicio

### 2.1 Aplicaciones (front, api-generica, api-facturas)
- `build: ./<carpeta>` — cada app tiene su Dockerfile propio.
- **Volumen de código** (`./front_flask:/app`, etc.) + `command:` con
  `--debug`/`--reload` → recarga en caliente sin reconstruir.
- `restart: unless-stopped`.
- Variables de entorno:
  - front: `API_GENERICA_URL=http://api-generica:8001`, `API_FACTURAS_URL=http://api-facturas:8002`.
  - APIs: `DB_PROVIDER: ${DB_PROVIDER:-postgres}` (interpolación con default → la
    variable del shell del host decide el motor) y las 4 cadenas SQLAlchemy async:
    ```
    DB_POSTGRES:  postgresql+asyncpg://paradigmas:paradigmas123@postgres:5432/bdfacturas_postgres_local
    DB_MARIADB:   mysql+aiomysql://paradigmas:paradigmas123@mariadb:3306/bdfacturas_mariadb_local
    DB_MYSQL:     (igual a DB_MARIADB, alias)
    DB_SQLSERVER: mssql+aioodbc://sa:Paradigmas123!@sqlserver:1433/bdfacturas_sqlserver_local?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
    ```
- El front monta además `.:/workspace:cached` para que el devcontainer vea el repo completo.
- No se usa `depends_on` entre apps y motores: las APIs crean el engine de forma
  perezosa (primera petición), así que toleran que la BD tarde en arrancar.

### 2.2 Motores de base de datos
- **postgres:** imagen `postgres:16-alpine`; `POSTGRES_DB/USER/PASSWORD`; monta
  `./db/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro` (el entrypoint
  oficial lo ejecuta solo si el volumen `pgdata` está vacío); healthcheck `pg_isready`.
- **mariadb:** imagen `mariadb:11`; `MARIADB_ROOT_PASSWORD/DATABASE/USER/PASSWORD`;
  mismo mecanismo de init con `./db/mariadb/init.sql`; healthcheck
  `healthcheck.sh --connect --innodb_initialized`.
- **sqlserver:** imagen `mcr.microsoft.com/mssql/server:2022-latest`;
  `ACCEPT_EULA=Y`, `MSSQL_SA_PASSWORD`, `MSSQL_PID: Developer`; healthcheck con
  `sqlcmd -C -Q 'SELECT 1'` (flag `-C` = confiar en el certificado), `retries: 20`,
  `start_period: 30s` porque tarda en arrancar.
- **sqlserver-init:** misma imagen de SQL Server (trae sqlcmd);
  `depends_on: sqlserver: condition: service_healthy`; monta `./db/sqlserver:/scripts:ro`;
  `entrypoint: ["/bin/bash", "/scripts/init.sh"]`; `restart: "no"` (corre y muere).
  Razón: la imagen de SQL Server **no tiene** `/docker-entrypoint-initdb.d`, hay
  que inicializar desde fuera.
- Puertos host desplazados: `15432:5432`, `13306:3306`, `11433:1433`.

### 2.3 phpMyAdmin
Imagen `phpmyadmin:latest`; `PMA_HOST=mariadb`, `PMA_USER/PMA_PASSWORD=paradigmas/paradigmas123`
(auto-login, sin pantalla de credenciales); `8081:80`; `depends_on: mariadb`.

### 2.4 Volúmenes
`volumes:` nombrados al final: `pgdata`, `mariadbdata`, `mssqldata`.

## 3. Scripts de base de datos (db/)

Los tres scripts crean el **mismo contenido** en tres dialectos:

1. **12 tablas** en orden de dependencias: primero las independientes
   (empresa, persona, producto, rol, ruta, usuario), luego las que tienen FK
   (cliente, vendedor, factura, productosporfactura, rol_usuario, rutarol).
   `productosporfactura` con PK compuesta y `ON DELETE CASCADE` desde factura;
   `rutarol` con CASCADE en ambas FK.
2. **Datos de ejemplo:** 3 empresas, 6 personas, 8 productos, 5 roles, 15 rutas,
   8 usuarios (con hashes BCrypt), 4 clientes, 3 vendedores, 6 facturas,
   12 renglones de detalle, roles por usuario y permisos rutarol.
   En PostgreSQL, tras insertar con id explícito, sincronizar secuencias con `setval`.
3. **Trigger** `actualizar_totales_y_stock` sobre productosporfactura
   (BEFORE INSERT/UPDATE/DELETE): valida stock suficiente, calcula subtotal
   (cantidad × valorunitario), ajusta stock del producto y recalcula el total de la factura.
4. **Procedimientos almacenados** (retornan JSON por parámetro INOUT en PostgreSQL;
   equivalentes con OUT/SELECT en los otros dialectos):
   - Facturas: `sp_insertar_factura_y_productosporfactura`, `sp_consultar_...`,
     `sp_listar_...`, `sp_actualizar_...`, `sp_borrar_...`, `sp_anular_factura`
     (borrado lógico: estado='anulada' + restaurar stock).
   - Usuarios: `crear_usuario_con_roles`, `actualizar_usuario_con_roles`,
     `eliminar_usuario_con_roles`, `actualizar_roles_usuario`,
     `consultar_usuario_con_roles`, `listar_usuarios_con_roles`.
   - RBAC: `verificar_acceso_ruta`, `listar_rutarol`, `crear_rutarol`, `eliminar_rutarol`.

Particularidades por dialecto:
- **PostgreSQL:** `SERIAL`, `plpgsql`, JSON nativo, `CREATE PROCEDURE` (PG 11+).
- **MariaDB:** `CREATE DATABASE IF NOT EXISTS` + `USE` + `SET NAMES utf8mb4` al
  inicio; `DROP ... IF EXISTS` de todos los objetos para que el script sea
  re-ejecutable; `AUTO_INCREMENT`; `DELIMITER` para triggers/SP.
- **SQL Server:** T-SQL con `IDENTITY`, `SET IDENTITY_INSERT`, `OUTPUT`/`FOR JSON`;
  el script asume la BD ya creada (la crea `init.sh`).

`init.sh` (bash): consulta `sys.databases` con sqlcmd; si la BD existe, sale con 0;
si no, `CREATE DATABASE` + ejecutar `bdfacturas.sql` con `-d $DB -i`.

## 4. Devcontainer (.devcontainer/devcontainer.json)

- `dockerComposeFile: ../docker-compose.yml`, `service: front`,
  `workspaceFolder: /workspace` (por eso el front monta el repo ahí).
- `forwardPorts: [8000, 8001, 8002]` con etiquetas.
- Extensiones: `ms-python.python`, `ms-python.vscode-pylance`, `mtxr.sqltools`
  + drivers `sqltools-driver-pg`, `-mysql`, `-mssql`.
- `sqltools.connections`: 3 conexiones con **hosts internos y puertos estándar**
  (`postgres:5432`, `mariadb:3306`, `sqlserver:1433` con
  `encrypt + trustServerCertificate`), porque VS Code corre DENTRO de la red de compose.

## 5. Orden de arranque real (qué pasa en `up -d --build`)

1. Docker construye las 3 imágenes de apps (la de api_* instala msodbcsql18, tarda más).
2. Los 3 motores arrancan en paralelo; Postgres/MariaDB ejecutan su init.sql si el
   volumen está vacío.
3. `sqlserver-init` espera el healthcheck de sqlserver y crea/llena la BD si no existe.
4. front y APIs arrancan de inmediato (no esperan a las BD); la primera petición
   que necesite datos crea el engine y conecta.
5. phpMyAdmin arranca tras mariadb.

## 6. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| SQL Server necesita ~2 GB RAM | El resto del stack no depende de él; documentar trabajar solo con postgres/mariadb |
| Puertos 8000/8081 ocupados en el host | Cambiar el mapeo en compose (documentado en la guía del estudiante) |
| init.sql corre solo con volumen vacío | `docker compose down -v` como procedimiento oficial de reset |
| Cambios de esquema en db/*.sql no se aplican a volúmenes existentes | Mismo procedimiento: `down -v` + `up -d` |
