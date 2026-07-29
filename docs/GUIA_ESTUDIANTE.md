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

## Paso 5 — Programar

Abra la carpeta en VS Code: menú **File → Open Folder** → `proyecto_paradigmas`.

| Qué quiere hacer | Dónde |
|---|---|
| Escribir la API en Python | carpeta `api/` — al guardar, la API se recarga sola |
| Escribir el frontend (HTML/JS) | carpeta `front/` — recargue el navegador para ver los cambios |

**Hasta aquí llega la puesta en marcha.** Lo que sigue es material de consulta para más adelante.

---

## Administrar las bases de datos (más adelante)

Cuando necesite explorar tablas y ejecutar SQL con clics:

1. Instale la extensión **Dev Containers** (`Ctrl+Shift+X` → buscar "Dev Containers" → Install).
2. Con la carpeta del proyecto abierta: `F1` → **Dev Containers: Reopen in Container**.
3. Aparece el icono de **SQLTools** (cilindro) con las 3 conexiones ya configuradas. `Ctrl+E Ctrl+E` ejecuta la consulta seleccionada.

También puede usar cualquier herramienta externa (DBeaver, HeidiSQL, SSMS) con las credenciales de abajo.

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
