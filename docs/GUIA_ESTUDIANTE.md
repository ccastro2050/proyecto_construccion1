# Guía del estudiante — Proyecto Construcción 1

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
git clone https://github.com/ccastro2050/proyecto_construccion1.git
```

## Paso 3 — Levantar todo (el único comando)

```powershell
cd proyecto_construccion1
docker compose up -d --build
```

> La **primera vez tarda varios minutos**. Las siguientes veces arranca en segundos.

## Paso 4 — Verificar

Abra en el navegador: **http://localhost:8000** — es el **frontend Flask**. Debe ver las dos APIs con la insignia verde "en línea" (la primera vez pueden tardar 1–2 minutos mientras arranca todo).

## Paso 5 — Su primer recorrido por las 3 capas

En http://localhost:8000:

1. Clic en **Productos** → la tabla que ve la pidió el front a una **API** y la API la leyó de la **base de datos**. Tres capas trabajando.
2. Cree un producto con el botón **Nuevo producto**, edítelo y elimínelo — es un CRUD completo.
3. En el menú superior derecho cambie la **API activa** (Genérica ↔ Facturas) y repita: la pantalla funciona igual con las dos. El front no depende de cómo está construido el backend.
4. Abra el **Explorador** y mire cualquiera de las 12 tablas de la base de datos.
5. Mire las APIs por dentro (documentación interactiva):
   - API Genérica: http://localhost:8001/swagger
   - API Facturas: http://localhost:8002/docs

## Paso 6 — Programar

Abra la carpeta en VS Code: menú **File → Open Folder** → `proyecto_construccion1`. Todo el código está comentado en español. Al guardar un archivo, la aplicación se recarga sola.

| Qué quiere tocar | Dónde |
|---|---|
| El frontend (pantallas, rutas Flask) | carpeta `front_flask/` |
| La API genérica (un CRUD para toda tabla) | carpeta `api_generica/` |
| La API de facturas (un CRUD por entidad) | carpeta `api_facturas/` |

> Para entender cómo se conecta todo, lea [ARQUITECTURA_3_CAPAS.md](ARQUITECTURA_3_CAPAS.md) y
> [PRINCIPIOS_SOLID_ACID.md](PRINCIPIOS_SOLID_ACID.md) (dónde está aplicado cada principio, con ejercicios).
>
> ¿Quiere reconstruir una pieza desde cero (o pedírselo a una IA)? Cada componente tiene su
> **spec kit** (especificación → plan → tareas): [proyecto e infraestructura](spec_kit/2_spec.md),
> [API Genérica](../api_generica/docs/spec_kit/2_spec.md),
> [API Facturas](../api_facturas/docs/spec_kit/2_spec.md) y
> [Front Flask](../front_flask/docs/spec_kit/2_spec.md).

## Paso 7 — Cambiar el motor de base de datos

Las APIs arrancan usando PostgreSQL. Para que usen otro motor:

```powershell
$env:DB_PROVIDER = "mariadb";  docker compose up -d
```

(opciones: `postgres`, `mariadb`, `sqlserver`). Recargue el front: los datos ahora salen del otro motor y **nada más cambió**.

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
2. General → Name: `Construccion1 Docker`
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
docker compose logs front    # errores del front (o api-generica / api-facturas)
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
| http://localhost:8000 no abre | `docker compose ps` para ver si los contenedores corren; `docker compose logs front` para ver el error |
| El puerto 8000 está ocupado | Cierre el otro programa que lo usa, o cambie el puerto en `docker-compose.yml` |
| Todo se dañó y quiero empezar de cero | `docker compose down -v` y luego `docker compose up -d --build` |
