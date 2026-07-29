# Tutorial — Cómo se construyó este proyecto

Pasos con los que se armó el entorno, con la explicación y el concepto detrás de cada uno. Sirve como guía si quiere **replicar este montaje** para otro proyecto o entender por qué cada archivo existe.

---

## Paso 1 — Clonar el repositorio y verificar Docker

```bash
git clone https://github.com/ccastro2050/proyecto_paradigmas.git
cd proyecto_paradigmas
docker --version
```

**Explicación:** se parte de un repositorio vacío en GitHub que será la forma de distribuir el entorno a los estudiantes.
**Concepto:** *Git como canal de distribución* — el repo no lleva solo código: lleva la definición completa del entorno (infraestructura como código).

## Paso 2 — Copiar los scripts SQL de la base de datos

```
db/
├── postgres/init.sql        (bdfacturas_postgres.sql)
├── mariadb/init.sql         (bdfacturas_mysql_mariadb.sql)
└── sqlserver/bdfacturas.sql (bdfacturas_sqlserver.sql)
```

**Explicación:** la misma base de datos `bdfacturas` está escrita en el dialecto de cada motor. Se colocan donde cada contenedor las buscará al arrancar.
**Concepto:** *scripts de inicialización* — las imágenes oficiales de PostgreSQL y MariaDB ejecutan automáticamente los `.sql` que encuentren en la carpeta `/docker-entrypoint-initdb.d`, **solo la primera vez** (cuando el volumen de datos está vacío).

## Paso 3 — Crear `docker-compose.yml`

Define 5 servicios: `app` (Python), `postgres`, `mariadb`, `sqlserver` y `sqlserver-init`.

Puntos clave del archivo:

| Elemento | Para qué |
|---|---|
| `volumes:` con nombre (`pgdata`, `mariadbdata`, `mssqldata`) | Los datos persisten al apagar los contenedores |
| Montaje `./db/...:/docker-entrypoint-initdb.d/...` | Carga automática de la BD en el primer arranque |
| `healthcheck:` | Docker sabe cuándo cada BD está realmente lista, no solo "encendida" |
| `depends_on: condition: service_healthy` | `sqlserver-init` espera a que SQL Server esté sano antes de crear la BD |
| `ports: "15432:5432"` etc. | Puertos alternativos hacia el PC para no chocar con instalaciones locales |
| Variables de entorno con las URL de conexión | El código Python no tiene credenciales quemadas: las recibe del entorno |

**Concepto:** *orquestación* — un solo archivo declara toda la infraestructura; `docker compose up` la materializa idéntica en cualquier máquina.

**Caso especial — SQL Server:** su imagen **no** tiene carpeta de inicialización automática. Solución: un contenedor auxiliar (`sqlserver-init`) que ejecuta `db/sqlserver/init.sh`: verifica si la BD existe, y solo si no existe la crea con `sqlcmd` y corre el script. Así los reinicios no borran datos (*idempotencia*).

## Paso 4 — Crear el Dev Container

Dos archivos en `.devcontainer/`:

**`Dockerfile`** — imagen del entorno de desarrollo:

```dockerfile
FROM python:3.12-slim
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
WORKDIR /workspace
```

Las librerías se instalan **en la imagen** para que el arranque sea rápido.

**`devcontainer.json`** — le dice a VS Code:

- `service: app` → trabajar dentro del contenedor `app` del compose.
- `extensions:` → instalar solo Python + SQLTools con sus 3 drivers.
- `settings.sqltools.connections` → dejar las 3 conexiones de BD **preconfiguradas**.
- `postCreateCommand` → reinstalar dependencias si `requirements.txt` cambió.
- `forwardPorts: [8000]` → exponer la API al navegador del estudiante.

Además `.vscode/tasks.json` define una tarea con `"runOn": "folderOpen"` que **arranca la API automáticamente** al abrir el proyecto.

**Concepto:** *entorno reproducible* — la configuración del editor también es código versionado; el estudiante no configura nada a mano.

## Paso 5 — Crear la API y el frontend de ejemplo

**`api/db.py`** — un *engine* de SQLAlchemy por motor; la URL define dialecto y driver:

```
postgresql+psycopg2://...   mysql+pymysql://...   mssql+pymssql://...
```

**`api/main.py`** — FastAPI con el motor como parámetro de la URL (`/api/{motor}/...`): salud de las 3 conexiones, listar tablas, CRUD de productos con **consultas parametrizadas**, JOIN de 5 tablas y un endpoint de SQL libre para prácticas.

**`front/index.html`** — HTML + JavaScript puro con `fetch()`: selector de motor, semáforo de conexiones y caja de SQL.

**Conceptos:** *API REST* (recursos + verbos HTTP + JSON), *consultas parametrizadas* (previenen inyección SQL), *portabilidad* — el mismo código sirve para los 3 motores porque solo cambia la URL de conexión.

## Paso 6 — Archivos de soporte

| Archivo | Para qué |
|---|---|
| `requirements.txt` | Dependencias de Python (FastAPI, SQLAlchemy y los 3 drivers) |
| `.gitignore` | No versionar `__pycache__`, `.venv`, `.env` |
| `.gitattributes` | Forzar fin de línea **LF** en `.sh` y `.sql` — un script con CRLF de Windows falla dentro de un contenedor Linux |

**Concepto:** *fines de línea* — Windows usa CRLF y Linux LF; como los scripts se ejecutan en contenedores Linux pero los estudiantes clonan en Windows, `.gitattributes` garantiza el formato correcto.

## Paso 7 — Probar todo antes de publicar

```bash
docker compose config --quiet        # el YAML es válido
docker compose up -d --build         # levantar los 5 servicios
docker compose logs sqlserver-init   # ¿la BD de SQL Server se creó?
docker compose exec postgres psql -U paradigmas -d bdfacturas_postgres_local -c "SELECT COUNT(*) FROM producto;"
docker compose exec mariadb mariadb -uparadigmas -pparadigmas123 bdfacturas_mariadb_local -e "SELECT COUNT(*) FROM factura;"
curl http://localhost:8000/api/salud # {"postgres":"ok","mariadb":"ok","sqlserver":"ok"}
curl http://localhost:8000/api/sqlserver/productos
```

**Concepto:** *verificación end-to-end* — no basta con que los contenedores "arranquen": se comprueba que los datos existen y que la API responde contra los tres motores antes de entregar a los estudiantes.

## Paso 8 — Publicar en GitHub

```bash
git add -A
git commit -m "Entorno Docker completo: devcontainer + PostgreSQL/MariaDB/SQL Server + API FastAPI + front (bdfacturas)"
git push -u origin main
```

A partir de aquí, cualquier estudiante reproduce el entorno completo con `git clone` + "Reopen in Container".

---

## Resumen de la arquitectura resultante

```
git clone  ──►  VS Code + Dev Containers  ──►  docker compose (automático)
                                                    │
                     ┌──────────────┬───────────────┼───────────────┬──────────────────┐
                     ▼              ▼               ▼               ▼                  ▼
                   app          postgres         mariadb        sqlserver       sqlserver-init
              (Python, API,   (init.sql se     (init.sql se    (motor 2022)    (crea la BD solo
               front, VS Code  autoejecuta)     autoejecuta)                    la primera vez)
               trabaja aquí)
```

| Decisión de diseño | Razón |
|---|---|
| Dev Container en vez de instrucciones de instalación | Un clic; imposible que "en mi máquina no funciona" |
| Un contenedor por motor de BD | Aislamiento; se puede apagar o resetear cada uno por separado |
| Contenedor auxiliar para SQL Server | Su imagen no soporta scripts de inicialización automática |
| Volúmenes con nombre | El trabajo de los estudiantes sobrevive a los reinicios |
| Credenciales simples en texto plano | Es un entorno **local de aprendizaje**; en producción irían en secretos |
| Puertos alternativos hacia el host (15432/13306/11433) | No chocar con MySQL/PostgreSQL ya instalados en el PC |
