# Guía del estudiante — Proyecto Paradigmas

Pasos para dejar el entorno funcionando en su máquina. Cada paso tiene una explicación corta de **qué hace** y **por qué**.

---

## Paso 0 — Instalar (solo la primera vez)

1. Instale **Docker Desktop para Windows**: https://docs.docker.com/desktop/setup/install/windows-install/
2. Instale **VS Code para Windows**: https://code.visualstudio.com/download
3. Instale **Git para Windows**: https://git-scm.com/download/win

> **Importante:** Docker Desktop debe estar **abierto** antes de continuar.

## Paso 1 — Abrir VS Code y su terminal

1. Abra **VS Code**.
2. Abra la terminal integrada: menú **Terminal → New Terminal** (o `Ctrl + ñ`).
3. En esa terminal ejecute:

```powershell
docker --version
```

**Qué hace:** muestra la versión de Docker. Si da error, Docker Desktop no está instalado o no está abierto.

> **Todos los comandos de esta guía se ejecutan en esa misma terminal de VS Code.**

## Paso 2 — Instalar la extensión Dev Containers

En la misma terminal de VS Code:

```powershell
code --install-extension ms-vscode-remote.remote-containers
```

**Qué hace:** agrega a VS Code la capacidad de trabajar "dentro" de un contenedor. Es la pieza que hace que todo se configure solo.

## Paso 3 — Clonar el repositorio

En la misma terminal:

```powershell
git clone https://github.com/ccastro2050/proyecto_paradigmas.git
```

**Qué hace:** descarga el proyecto completo a una carpeta `proyecto_paradigmas` en su máquina.

## Paso 4 — Abrir la carpeta del proyecto

En la misma terminal:

```powershell
cd proyecto_paradigmas
code . -r
```

**Qué hace:** entra a la carpeta y la abre en la ventana actual de VS Code.

## Paso 5 — Abrir dentro del contenedor (el paso clave)

Presione `F1`, escriba y seleccione:

```
Dev Containers: Reopen in Container
```

**Qué hace:** VS Code lee el archivo `.devcontainer/devcontainer.json` y automáticamente:

1. Construye el contenedor de desarrollo con Python y todas las librerías.
2. Levanta **PostgreSQL, MariaDB y SQL Server** en contenedores.
3. Carga la base de datos **bdfacturas** en los tres motores (tablas + datos).
4. Instala las extensiones de VS Code (Python, SQLTools) con las conexiones ya configuradas.
5. Arranca la API de ejemplo en http://localhost:8000.

> La **primera vez tarda varios minutos** (descarga las imágenes). Las siguientes veces abre en segundos.
> Si VS Code pregunta si permite ejecutar tareas automáticas, responda **Allow** (es la tarea que arranca la API).

## Paso 6 — Verificar que todo funciona

| Verificación | Dónde |
|---|---|
| Frontend con semáforo de los 3 motores en verde | http://localhost:8000 |
| Documentación interactiva de la API (Swagger) | http://localhost:8000/docs |
| Explorar las bases de datos | Ícono de **SQLTools** (cilindro) en la barra lateral de VS Code |

> SQL Server es el más lento: puede tardar 1–2 minutos en ponerse en verde.

## Paso 7 — Programar

| Qué quiere hacer | Dónde |
|---|---|
| Escribir la API en Python | carpeta `api/` (al guardar, la API se recarga sola) |
| Escribir el frontend (HTML/JS) | carpeta `front/` |
| Ejecutar SQL contra cualquier motor | SQLTools (`Ctrl+E Ctrl+E` ejecuta la consulta seleccionada) |

---

## Comandos útiles del día a día

```bash
# Apagar todo (los datos de las BD se conservan)
docker compose down

# Volver a encender (sin abrir VS Code)
docker compose up -d

# Resetear las bases de datos a su estado original (¡borra sus cambios en las BD!)
docker compose down -v
docker compose up -d

# Ver el estado de los contenedores
docker compose ps

# Arrancar la API manualmente (dentro del contenedor, si la cerró)
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Credenciales de las bases de datos

| Motor | Base de datos | Usuario | Contraseña | Puerto en su PC |
|---|---|---|---|---|
| PostgreSQL | `bdfacturas_postgres_local` | `paradigmas` | `paradigmas123` | `15432` |
| MariaDB | `bdfacturas_mariadb_local` | `paradigmas` | `paradigmas123` | `13306` |
| SQL Server | `bdfacturas_sqlserver_local` | `sa` | `Paradigmas123!` | `11433` |

> Dentro del contenedor (código Python y SQLTools) los hosts son `postgres`, `mariadb` y `sqlserver` con los puertos estándar. Los puertos de la tabla son solo si quiere conectarse con una herramienta externa (DBeaver, HeidiSQL, SSMS).

## Problemas frecuentes

| Problema | Solución |
|---|---|
| No aparece "Reopen in Container" | Verifique que Docker Desktop esté abierto y la extensión Dev Containers instalada; luego `F1` → *Dev Containers: Reopen in Container* |
| SQL Server "sin conexión" | Espere 1–2 minutos; necesita ~2 GB de RAM. En equipos limitados trabaje solo con PostgreSQL y MariaDB |
| El puerto 8000 está ocupado | Cierre el otro programa que lo usa, o cambie el puerto en `docker-compose.yml` |
| Todo se dañó y quiero empezar de cero | `docker compose down -v` y luego reabrir en el contenedor |
