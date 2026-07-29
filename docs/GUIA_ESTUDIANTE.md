# Guía del estudiante — Proyecto Paradigmas

Pasos para dejar el entorno funcionando en su máquina.

---

## Paso 0 — Instalar (solo la primera vez)

1. Instale **Docker Desktop para Windows**: https://docs.docker.com/desktop/setup/install/windows-install/
2. Instale **VS Code para Windows**: https://code.visualstudio.com/download
3. Instale **Git para Windows**: https://git-scm.com/download/win

> **Importante:** Docker Desktop debe estar **abierto** antes de continuar.

## Paso 1 — Abrir VS Code y su terminal

1. Abra **VS Code**.
2. Abra la terminal integrada: menú **Terminal → New Terminal** (o `Ctrl + ñ`).
3. Verifique que Docker responde:

```powershell
docker --version
```

Si da error, Docker Desktop no está abierto.

## Paso 2 — Clonar el proyecto

En la misma terminal:

```powershell
git clone https://github.com/ccastro2050/proyecto_paradigmas.git
```

## Paso 3 — Levantar todo (el único comando)

```powershell
cd proyecto_paradigmas
docker compose up -d --build
```

> La **primera vez tarda varios minutos**. Las siguientes veces arranca en segundos.

## Paso 4 — Verificar

Abra en el navegador: **http://localhost:8000** — debe ver los 3 motores en verde (SQL Server tarda 1–2 minutos).

## Paso 5 — Su primera consulta contra una base de datos

En esa misma página (http://localhost:8000):

1. En **Motor** deje `PostgreSQL` y haga clic en el botón **Productos** → la tabla que aparece viene de la base de datos PostgreSQL, consultada en vivo por la API de Python.
2. Clic en **Facturas (JOIN)** → una consulta que une 5 tablas.
3. En la caja de texto escriba una consulta y clic en **Ejecutar SQL**:

```sql
SELECT * FROM persona
```

4. Ahora cambie **Motor** a `MariaDB` o `SQL Server` y repita: **es la misma base de datos y el mismo código Python, pero otro motor**. De eso se trata el curso.

También puede verlo desde la terminal:

```powershell
curl http://localhost:8000/api/postgres/productos
```

## Paso 6 — Programar

Abra la carpeta en VS Code: menú **File → Open Folder** → `proyecto_paradigmas`.

| Qué quiere hacer | Dónde |
|---|---|
| Escribir la API en Python | carpeta `api/` — al guardar, la API se recarga sola |
| Escribir el frontend (HTML/JS) | carpeta `front/` — recargue el navegador para ver los cambios |

**Hasta aquí llega la puesta en marcha.** Lo que sigue es material de consulta para más adelante.

---

## Cuando vuelva (la próxima clase)

La descarga grande fue **una sola vez**. Para retomar el trabajo:

1. Abra **Docker Desktop** y espere a que arranque.
2. En la terminal de VS Code, dentro de la carpeta del proyecto:

```powershell
docker compose up -d
```

Arranca en **segundos** y con **todos sus datos intactos**.

**Por qué:** las imágenes ya quedaron descargadas en su PC, y los datos de las bases de datos viven en **volúmenes** de Docker — un disco persistente que sobrevive a apagar los contenedores e incluso a reiniciar el computador. Solo se borran si usted lo pide con `docker compose down -v`.

Casos especiales:

```powershell
# El profesor publicó cambios en el repositorio
git pull
docker compose up -d --build

# Quiere las BD como nuevas (borra lo que usted insertó o modificó)
docker compose down -v
docker compose up -d
```

---

## Administrar las bases de datos (más adelante)

### Lo más fácil: phpMyAdmin (ya incluido, para MariaDB)

Abra **http://localhost:8081** — entra directo, sin usuario ni clave. Ahí puede ver las tablas de `bdfacturas_mariadb_local`, editar datos y ejecutar SQL. Viene como un contenedor más del proyecto: no hay que instalar nada (ni XAMPP).

### Desde VS Code con SQLTools (los 3 motores)

Cuando necesite explorar tablas y ejecutar SQL con clics:

1. Instale la extensión **Dev Containers** (`Ctrl+Shift+X` → buscar "Dev Containers" → Install).
2. Con la carpeta del proyecto abierta: `F1` → **Dev Containers: Reopen in Container**.
3. Aparece el icono de **SQLTools** (cilindro) con las 3 conexiones ya configuradas. `Ctrl+E Ctrl+E` ejecuta la consulta seleccionada.

### Con herramientas instaladas en su PC

También puede usar cualquier herramienta externa con las credenciales de abajo. Por ejemplo:

**pgAdmin (PostgreSQL):**
1. Clic derecho en **Servers → Register → Server…**
2. General → Name: `Paradigmas Docker`
3. Connection → Host: `localhost` · Port: **`15432`** · Maintenance database: `bdfacturas_postgres_local` · Username: `paradigmas` · Password: `paradigmas123` (marque *Save password*)
4. **Save** → navegue: Databases → bdfacturas_postgres_local → Schemas → public → Tables

**HeidiSQL / MySQL Workbench (MariaDB):** host `localhost`, puerto **`13306`**, usuario `paradigmas`, clave `paradigmas123`.

**SSMS / Azure Data Studio (SQL Server):** servidor `localhost,11433`, usuario `sa`, clave `Paradigmas123!` (marque *Trust server certificate*).

> Se usan los puertos 15432/13306/11433 porque así están mapeados los contenedores hacia su PC, para no chocar con motores que ya tenga instalados.

## Comandos útiles del día a día

```powershell
docker compose down          # apagar todo (los datos se conservan)
docker compose up -d         # volver a encender
docker compose down -v       # resetear las BD a su estado original (¡borra sus cambios!)
docker compose ps            # ver el estado de los contenedores
docker compose logs app      # ver los errores de la API si algo falla
```

## Credenciales de las bases de datos

| Motor | Base de datos | Usuario | Contraseña | Puerto en su PC |
|---|---|---|---|---|
| PostgreSQL | `bdfacturas_postgres_local` | `paradigmas` | `paradigmas123` | `15432` |
| MariaDB | `bdfacturas_mariadb_local` | `paradigmas` | `paradigmas123` | `13306` |
| SQL Server | `bdfacturas_sqlserver_local` | `sa` | `Paradigmas123!` | `11433` |

> Esos puertos son para herramientas externas (DBeaver, HeidiSQL, SSMS). Dentro de los contenedores (código Python y SQLTools) los hosts son `postgres`, `mariadb` y `sqlserver` con los puertos estándar.

## Problemas frecuentes

| Problema | Solución |
|---|---|
| SQL Server "sin conexión" | Espere 1–2 minutos; necesita ~2 GB de RAM. En equipos limitados trabaje solo con PostgreSQL y MariaDB |
| http://localhost:8000 no abre | `docker compose ps` para ver si los contenedores corren; `docker compose logs app` para ver el error |
| El puerto 8000 está ocupado | Cierre el otro programa que lo usa, o cambie el puerto en `docker-compose.yml` |
| Todo se dañó y quiero empezar de cero | `docker compose down -v` y luego `docker compose up -d --build` |
