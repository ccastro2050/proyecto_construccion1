# Guía del estudiante — Proyecto Paradigmas

## Paso 1 — Instalar

1. Instale **Docker Desktop**: https://www.docker.com/products/docker-desktop/
2. Instale **VS Code**: https://code.visualstudio.com/
3. Instale **Git**: https://git-scm.com/

Abra Docker Desktop y déjelo abierto.

## Paso 2 — Instalar la extensión Dev Containers

En PowerShell:

```powershell
code --install-extension ms-vscode-remote.remote-containers
```

## Paso 3 — Clonar el proyecto

```powershell
git clone https://github.com/ccastro2050/proyecto_paradigmas.git
```

## Paso 4 — Abrirlo en VS Code

```powershell
cd proyecto_paradigmas
code .
```

## Paso 5 — Abrir dentro del contenedor

En VS Code presione `F1`, escriba y seleccione:

```
Dev Containers: Reopen in Container
```

Espere (la primera vez tarda varios minutos). Si pregunta por tareas automáticas, responda **Allow**.

## Paso 6 — Verificar

- http://localhost:8000 → frontend con los 3 motores en verde (SQL Server tarda 1–2 minutos)
- http://localhost:8000/docs → documentación de la API
- Ícono de **SQLTools** (cilindro) en VS Code → las 3 bases de datos

## Paso 7 — Programar

- API Python → carpeta `api/` (se recarga sola al guardar)
- Frontend → carpeta `front/`
- SQL → SQLTools (`Ctrl+E Ctrl+E` ejecuta la consulta seleccionada)

---

## Comandos útiles

```bash
docker compose down       # apagar (los datos se conservan)
docker compose up -d      # encender
docker compose down -v    # resetear las BD a su estado original
docker compose ps         # ver estado
```

## Credenciales

| Motor | Base de datos | Usuario | Contraseña | Puerto en su PC |
|---|---|---|---|---|
| PostgreSQL | `bdfacturas_postgres_local` | `paradigmas` | `paradigmas123` | `15432` |
| MariaDB | `bdfacturas_mariadb_local` | `paradigmas` | `paradigmas123` | `13306` |
| SQL Server | `bdfacturas_sqlserver_local` | `sa` | `Paradigmas123!` | `11433` |

> Desde el código y SQLTools los hosts son `postgres`, `mariadb` y `sqlserver` (puertos estándar). Los puertos de la tabla son solo para herramientas externas (DBeaver, HeidiSQL, SSMS).

## Problemas frecuentes

| Problema | Solución |
|---|---|
| No aparece "Reopen in Container" | Docker Desktop debe estar abierto; `F1` → *Dev Containers: Reopen in Container* |
| SQL Server "sin conexión" | Espere 1–2 minutos (necesita ~2 GB de RAM) |
| Quiero empezar de cero | `docker compose down -v` y reabrir en el contenedor |
