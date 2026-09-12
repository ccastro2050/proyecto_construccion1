# Conceptos de Docker — imagen, contenedor, volumen, compose y Kubernetes

> Documento conceptual del curso. Este proyecto levanta **10 contenedores con
> un solo comando** (`docker compose up -d --build`): 2 fronts, 3 APIs, 3
> motores de base de datos, un administrador web y un inicializador. Aquí está
> el mapa de conceptos que hace posible eso, con los ejemplos de ESTE
> proyecto.

---

## 1. ¿Qué problema resuelve Docker?

"En mi máquina sí funciona." Cada estudiante tiene un PC distinto (Windows,
versiones, configuraciones) y un software como PostgreSQL o SQL Server
instalado a mano se comporta distinto en cada uno. Docker empaqueta el
software **con todo su entorno** en una unidad estándar que corre igual en
cualquier máquina. En este curso nadie instala PostgreSQL, MariaDB, SQL
Server, Python ni .NET: todos corren **los mismos contenedores**.

## 2. Imagen

Una imagen es una **plantilla inmutable y empaquetada**: un sistema de
archivos congelado (SO base + programa + librerías + configuración) más
metadatos (qué comando arrancar, qué puerto expone).

- **Inmutable**: una vez construida, no cambia. Cambiar algo = construir OTRA imagen.
- Se construye en **capas** (cada instrucción de un `Dockerfile` es una capa
  que se cachea — por eso las reconstrucciones son rápidas).
- Viene de un **registro** (Docker Hub) o se construye localmente. Este
  proyecto usa de ambas: `postgres:16-alpine`, `mariadb:11`,
  `mcr.microsoft.com/mssql/server:2022-latest` y `phpmyadmin:latest` vienen
  del registro (el `:16-alpine` es la **etiqueta**: versión 16, variante
  liviana Alpine); las de las 3 APIs y los 2 fronts **se construyen** con el
  `Dockerfile` de cada carpeta.

**Analogía:** la imagen es el **molde de la galleta**.

### 2.1 El `Dockerfile`: la receta de la imagen

Una imagen no aparece sola: **alguien escribe cómo se arma**. Ese «cómo»
va en un archivo llamado `Dockerfile` (sin extensión), y este proyecto
tiene 5: `./front_flask`, `./api_generica`, `./api_facturas`, `./api_generica_csharp`, `./front_blazor`.

Este es el de `api-generica`, sin los comentarios para verlo de un vistazo:

```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl gnupg2 ca-certificate…
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8011"]
```

Esto hace cada instrucción:

| Instrucción | Qué hace | Por qué está aquí |
|---|---|---|
| `FROM python:3.12-slim` | **De dónde se parte.** Toma una imagen ya hecha | Nadie arma un sistema desde cero: se parte de una que ya trae lo básico |
| `RUN apt-get update && apt-get install -y --…` | **Ejecuta algo AL CONSTRUIR** la imagen, una sola vez | Lo que instale aquí queda **dentro** de la imagen |
| `WORKDIR /app` | La carpeta donde se trabaja dentro del contenedor | Para no repetir la ruta completa en cada instrucción siguiente |
| `COPY requirements.txt .` | **Copia archivos** de su computador hacia adentro de la imagen | Así la imagen se lleva la aplicación |
| `CMD ["uvicorn", "main:app", "--host", "0.0.…` | **El comando que se ejecuta al encender** el contenedor | Si ese proceso termina, el contenedor se apaga |

**La diferencia entre `RUN` y `CMD`** es la que más se confunde:

| | Cuándo corre | Cuántas veces |
|---|---|---|
| `RUN` | Al **construir** la imagen (`--build`) | Una sola vez, y queda guardado |
| `CMD` | Al **encender** el contenedor | Cada vez que arranca |


## 3. Contenedor

Un contenedor es una **instancia viva de una imagen**: un proceso corriendo
con su propio sistema de archivos, red y espacio de procesos, aislado del
resto de su PC.

- De una imagen salen **muchos contenedores** (galletas del mismo molde). En
  este proyecto pasa de verdad: `sqlserver` y `sqlserver-init` son DOS
  contenedores de la MISMA imagen de SQL Server — uno es el motor, el otro
  solo ejecuta el script de la BD y termina.
- Es **efímero y desechable**: `docker compose down` destruye los 10 sin
  drama, y `up -d` los recrea idénticos.
- **No es una máquina virtual**: no carga un sistema operativo completo —
  comparte el kernel del host con aislamiento de procesos. Por eso arrancan
  en segundos y pesan MB, no GB (la excepción de peso es SQL Server, que
  necesita ~2 GB de RAM por ser SQL Server, no por ser contenedor).

**Analogía:** el contenedor es la **galleta**.

## 4. Volumen (y el estado)

Si los contenedores son desechables… ¿dónde viven los datos? En
**almacenamiento que sobrevive al contenedor**:

| Mecanismo | Qué es | En este proyecto |
|---|---|---|
| **Volumen nombrado** | Espacio administrado por Docker, montado dentro del contenedor | `pgdata`, `mariadbdata`, `mssqldata` — los datos de los 3 motores (por eso `down`/`up` los conserva) |
| **Bind mount** | Una carpeta de SU disco montada dentro del contenedor | `./api_generica:/app` y similares — el código entra al contenedor desde su carpeta; guardar un archivo lo actualiza adentro al instante |
| **Volumen anónimo** | Un hueco sin nombre que "tapa" una subcarpeta del bind mount | `/app/bin` y `/app/obj` en los servicios .NET — los compilados de Linux quedan DENTRO del contenedor, sin mezclarse con los de Windows |

Detalle importante: los motores ejecutan su script `init.sql` **solo la
primera vez** (cuando su volumen está vacío). Por eso el "reset" de las BD es
`docker compose down -v` (la `-v` borra los volúmenes) y volver a subir — no
reiniciar.

**La regla de oro que ata los tres conceptos:** *la imagen es inmutable, el
contenedor es desechable, y el volumen es lo único que debe importarte
perder.*

```
Dockerfile   →  IMAGEN      →  CONTENEDOR   →  VOLUMEN
(receta)        (molde)        (galleta)       (la memoria)
             docker build    docker run       -v / volumes
```

> **La sorpresa que confunde a todo el mundo:** el volumen sobrevive
> INCLUSO a borrar la carpeta del proyecto. Si usted borra la carpeta,
> vuelve a hacer `git clone` y ejecuta `docker compose up -d --build`,
> la BD arranca **con los datos de la última vez** — no con las semillas.
> ¿Por qué? El volumen no vive en la carpeta: vive en el área de Docker,
> identificado por el nombre del proyecto compose (= el nombre de la
> carpeta). Misma carpeta → mismo nombre → mismo volumen de siempre.
>
> | Comando | ¿Y los datos? |
> |---|---|
> | `docker compose up -d --build` | Se conservan |
> | `docker compose down` | Se conservan |
> | borrar la carpeta y re-clonar | **Se conservan** (el volumen no estaba ahí) |
> | `docker compose down -v` | **SE BORRAN** — el único que resetea |
>
> Para una demo con las semillas exactas:
> `docker compose down -v` y luego `docker compose up -d --build`.

### El despliegue de ESTE proyecto, dibujado (Mermaid)

Todo lo anterior, junto: lo que `docker compose up -d` levanta aquí es un
**sistema de servidores en miniatura** — cada contenedor es un servidor
con su propio hostname, unidos por la red interna del compose:

```mermaid
flowchart LR
    NAV["Navegador / curl / Swagger"]
    subgraph PC["Su PC — Docker Desktop (el 'centro de datos')"]
        subgraph RED["red interna del compose (LAN virtual, con DNS propio)"]
            FRONT["SERVIDOR WEB (front)<br/>contenedor front<br/>hostname: front · escucha en 8010"]
            FRONTBLAZOR["SERVIDOR WEB (front)<br/>contenedor front-blazor<br/>hostname: front-blazor · escucha en 8014"]
            APIGENERICA["SERVIDOR DE APLICACIONES<br/>contenedor api-generica<br/>hostname: api-generica · escucha en 8011"]
            APIFACTURAS["SERVIDOR DE APLICACIONES<br/>contenedor api-facturas<br/>hostname: api-facturas · escucha en 8012"]
            APIGENERICACSHARP["SERVIDOR DE APLICACIONES<br/>contenedor api-generica-csharp<br/>hostname: api-generica-csharp · escucha en 8013"]
            PHPMYADMIN["SERVIDOR DE APLICACIONES<br/>contenedor phpmyadmin<br/>hostname: phpmyadmin · escucha en 80"]
            POSTGRES[("SERVIDOR DE BASE DE DATOS<br/>PostgreSQL · contenedor postgres<br/>hostname: postgres · escucha en 5432")]
            MARIADB[("SERVIDOR DE BASE DE DATOS<br/>MariaDB/MySQL · contenedor mariadb<br/>hostname: mariadb · escucha en 3306")]
            SQLSERVER[("SERVIDOR DE BASE DE DATOS<br/>SQL Server · contenedor sqlserver<br/>hostname: sqlserver · escucha en 1433")]
            SQLSERVERINIT["sqlserver-init<br/>siembra la BD UNA vez<br/>y muere: Exited(0) = éxito"]
        end
    end
    NAV -->|"localhost:8010"| FRONT
    NAV -->|"localhost:8014"| FRONTBLAZOR
    NAV -->|"localhost:8011"| APIGENERICA
    NAV -->|"localhost:8012"| APIFACTURAS
    NAV -->|"localhost:8013"| APIGENERICACSHARP
    NAV -->|"localhost:8091"| PHPMYADMIN
    FRONT -->|"consume la API por la LAN"| APIGENERICA
    FRONT -->|"consume la API por la LAN"| APIFACTURAS
    FRONT -->|"consume la API por la LAN"| APIGENERICACSHARP
    FRONT -->|"consume la API por la LAN"| PHPMYADMIN
    FRONTBLAZOR -->|"consume la API por la LAN"| APIGENERICA
    FRONTBLAZOR -->|"consume la API por la LAN"| APIFACTURAS
    FRONTBLAZOR -->|"consume la API por la LAN"| APIGENERICACSHARP
    FRONTBLAZOR -->|"consume la API por la LAN"| PHPMYADMIN
    APIGENERICA -->|"postgres:5432 (DNS de Docker)"| POSTGRES
    APIGENERICA -->|"mariadb:3306 (DNS de Docker)"| MARIADB
    APIGENERICA -->|"sqlserver:1433 (DNS de Docker)"| SQLSERVER
    APIFACTURAS -->|"postgres:5432 (DNS de Docker)"| POSTGRES
    APIFACTURAS -->|"mariadb:3306 (DNS de Docker)"| MARIADB
    APIFACTURAS -->|"sqlserver:1433 (DNS de Docker)"| SQLSERVER
    APIGENERICACSHARP -->|"postgres:5432 (DNS de Docker)"| POSTGRES
    APIGENERICACSHARP -->|"mariadb:3306 (DNS de Docker)"| MARIADB
    APIGENERICACSHARP -->|"sqlserver:1433 (DNS de Docker)"| SQLSERVER
    PHPMYADMIN -->|"postgres:5432 (DNS de Docker)"| POSTGRES
    PHPMYADMIN -->|"mariadb:3306 (DNS de Docker)"| MARIADB
    PHPMYADMIN -->|"sqlserver:1433 (DNS de Docker)"| SQLSERVER
    SQLSERVERINIT -->|"espera el healthcheck,<br/>siembra y termina"| SQLSERVER
    NAV -.->|"opcional (diagnóstico):<br/>localhost:15448"| POSTGRES
    NAV -.->|"opcional (diagnóstico):<br/>localhost:13316"| MARIADB
    NAV -.->|"opcional (diagnóstico):<br/>localhost:11443"| SQLSERVER
```

**Guía de lectura:** los servicios se hablan entre sí **por nombre**
(el DNS interno de Docker resuelve `postgres`, `api-facturas`, etc. a la
IP del contenedor — jamás `localhost`, que dentro de un contenedor es él
mismo). Hacia su PC solo existen las puertas `localhost:PUERTO` que el
compose publica. Por eso este mismo diseño se despliega igual en un
servidor real: cambiar de máquina no cambia la arquitectura.

## 5. Docker Compose (el "un solo comando" del proyecto)

¿Cómo levantar 10 contenedores sin escribir 10 comandos `docker run` con
todos sus flags, en el orden correcto, cada vez?

**Compose** es la respuesta **declarativa**: un archivo `docker-compose.yml`
(formato YAML) que declara el estado deseado del sistema completo — qué
servicios existen, de qué imagen sale cada uno, puertos, volúmenes, variables
y dependencias — y `docker compose up -d` lo materializa. Es **declarativo,
no imperativo**: usted no escribe los pasos, escribe el resultado; en cada
`up -d` Compose compara lo declarado con lo que corre y solo recrea lo que
cambió (el mismo espíritu de SDD: describir el QUÉ).

### El `docker-compose.yml` de ESTE proyecto, por piezas

El archivo completo está en la raíz; estas son sus piezas representativas
(cada patrón se repite en los demás servicios):

**Un motor de BD (imagen del registro + volumen + healthcheck):**

```yaml
  postgres:
    image: postgres:16-alpine      # imagen del registro (no se construye)
    environment:                   # variables que la imagen usa al crear la BD
      POSTGRES_DB: bdfacturas_postgres_local
      POSTGRES_USER: paradigmas
      POSTGRES_PASSWORD: paradigmas123
    volumes:
      - pgdata:/var/lib/postgresql/data              # volumen nombrado: los datos sobreviven
      - ./db/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
        # ↑ bind mount: SU script entra al contenedor (:ro = solo lectura) y
        #   se ejecuta SOLO la primera vez (volumen vacío) — el reset es `down -v`
    ports:
      - "15448:5432"               # "puerto en su PC : puerto interno del contenedor"
    healthcheck:                   # cómo saber si la BD ya RESPONDE (no solo "existe")
      test: ["CMD-SHELL", "pg_isready -U paradigmas -d bdfacturas_postgres_local"]
```

**Una API Python (imagen construida + código montado + hot-reload):**

```yaml
  api-generica:
    build: ./api_generica          # esta imagen SE CONSTRUYE con el Dockerfile de esa carpeta
    volumes:
      - ./api_generica:/app        # el código montado: guardar un .py recarga la API sola
    command: uvicorn main:app --host 0.0.0.0 --port 8011 --reload
      # ↑ sobreescribe el CMD del Dockerfile para agregar --reload (desarrollo)
    ports:
      - "8011:8011"                # http://localhost:8011/swagger
    environment:
      # El host es el NOMBRE del servicio (postgres:5432), no localhost:
      # dentro de la red interna de compose los servicios se resuelven por
      # nombre (DNS propio).
      DB_PROVIDER: ${DB_PROVIDER:-postgres}   # cambia de motor SIN tocar código
      DB_POSTGRES: postgresql+asyncpg://paradigmas:paradigmas123@postgres:5432/bdfacturas_postgres_local
```

**Un servicio .NET (los volúmenes anónimos + variables que sobreescriben appsettings):**

```yaml
  api-generica-csharp:
    build: ./api_generica_csharp
    volumes:
      - ./api_generica_csharp:/app   # el código montado: dotnet watch recompila al guardar
      - /app/bin                     # bin y obj quedan DENTRO del contenedor (Linux),
      - /app/obj                     #   sin mezclarse con los compilados de Windows
    ports:
      - "8013:8013"                  # http://localhost:8013/swagger
    environment:
      # ASP.NET Core lee "ConnectionStrings__X" como ConnectionStrings:X — estas
      # variables SOBREESCRIBEN los valores de appsettings.json dentro de Docker.
      DatabaseProvider: ${DB_PROVIDER:-postgres}
      ConnectionStrings__Postgres: "Host=postgres;Port=5432;Database=..."
```

**Una dependencia por salud (el front Blazor espera a su API):**

```yaml
  front-blazor:
    ports:
      - "8014:8014"
    environment:
      ApiBaseUrl: http://api-generica-csharp:8013   # host interno, no localhost
    depends_on:
      - api-generica-csharp          # orden de arranque
  # y en sqlserver-init, la versión fuerte:
  #   depends_on:
  #     sqlserver:
  #       condition: service_healthy # arranca cuando el motor RESPONDE, no por azar
```

Las tres ideas que este archivo demuestra:

1. **Dos redes de nombres**: hacia su PC, puertos publicados
   (`localhost:8010`…`8014`, `15448`, `13316`, `11443`, `8091`); entre
   contenedores, nombres de servicio (`postgres:5432`,
   `api-generica-csharp:8013`). El mismo servicio tiene dos "direcciones"
   según quién lo llame.
2. **Dependencias por salud**: `service_healthy` + healthcheck — el
   inicializador de SQL Server espera a que el motor responda, no a que el
   contenedor exista.
3. **Desarrollo dentro del contenedor**: código montado + `--reload` /
   `--debug` / `dotnet watch` = guardar recarga, sin reconstruir la imagen.
   Solo se reconstruye (`--build`) cuando cambian dependencias
   (`requirements.txt`, `.csproj`) o el Dockerfile.

### Contenedores huérfanos y `--remove-orphans`

Compose recuerda qué contenedores creó para este proyecto (los marca con el
nombre de la carpeta: `proyecto_construccion1-...`). Si el
`docker-compose.yml` **deja de declarar** un servicio que antes existía, su
contenedor no se borra solo: queda **huérfano** — creado por el proyecto,
pero ya sin servicio que lo respalde — y Compose lo avisa al arrancar:

```
Found orphan containers ([proyecto_construccion1-xxx-1 ...]) for this project.
```

Aquí puede pasar si usted elimina o renombra un servicio del compose (o si
agregó uno de prueba y luego lo quitó del archivo). No estorba para trabajar
(está detenido), pero ocupa disco y ensucia `docker ps -a`. La limpieza:

```powershell
docker compose up -d --remove-orphans   # levanta lo declarado Y borra los huérfanos
```

Importante: borra los **contenedores** sobrantes, no los **volúmenes** — los
datos de las BD siguen ahí (sección 4).

### Las directivas del `docker-compose.yml`, una por una

Estas son las palabras clave que usa el archivo de arriba, con lo que
significan y qué pasaría si faltaran:

| Directiva | Qué declara | Si no está |
|---|---|---|
| `services:` | La lista de contenedores del sistema. Cada nombre debajo es un servicio | No hay nada que levantar |
| `image:` | **Usa** una imagen ya hecha, del registro público | Habría que construirla con `build:` |
| `build:` | **Construye** la imagen con el `Dockerfile` de esa carpeta | Docker no sabría cómo armar su aplicación |
| `environment:` | Variables que el programa lee al arrancar (claves, direcciones) | El programa arranca sin saber a qué base conectarse |
| `volumes:` | Qué carpetas o volúmenes se montan dentro del contenedor | Los datos se pierden al apagar, y el código no se refresca |
| `ports:` | `"puerto en su PC : puerto dentro del contenedor"` | El servicio corre pero **usted no lo puede abrir** desde el navegador |
| `depends_on:` | En qué orden arrancan los servicios | Arrancan a la vez, y la API busca una base que todavía no existe |
| `healthcheck:` | Cómo saber si el servicio **ya responde**, no solo si «existe» | `depends_on` esperaría a que arranque, no a que sirva |
| `restart:` | Qué hacer si el proceso se muere | El contenedor se queda caído |
| `command:` | Reemplaza el `CMD` del Dockerfile para ese servicio | Se usa el del Dockerfile |
| `volumes:` (al final, sin indentar) | Declara los volúmenes **nombrados** que usan los servicios | El volumen no existe y el servicio no arranca |

**El nombre del servicio es también su dirección.** Cuando un servicio le
habla a otro, lo llama por el nombre que tiene en este archivo: Docker crea
una red interna y lo resuelve. Por eso no se usa `localhost` — **dentro de
un contenedor, `localhost` es el contenedor mismo**.

**Los dos números de `ports:` no son lo mismo.** El de la izquierda es el
puerto de su computador; el de la derecha, el de adentro. Cambiar el de la
izquierda no toca una línea de código.


### `docker compose up -d --build`: un comando que hace siete cosas

Esta es la parte que hace que valga la pena. **Un solo comando ejecuta toda
esta secuencia**, en este orden:

| # | Qué hace | El comando que se ahorra |
|---|---|---|
| 1 | **Lee** el `docker-compose.yml` y entiende el sistema completo | — |
| 2 | **Descarga** las imágenes que usted no tiene todavía (las de `image:`) | `docker pull imagen` por cada una |
| 3 | **Construye** las imágenes propias siguiendo su `Dockerfile` (las de `build:`) | `docker build -t nombre ./carpeta` por cada una |
| 4 | **Crea la red** interna para que los contenedores se encuentren por su nombre | `docker network create red` |
| 5 | **Crea los volúmenes** nombrados donde viven los datos | `docker volume create nombre` |
| 6 | **Crea y enciende un contenedor por servicio**, con sus puertos, variables y volúmenes | `docker run -d --name … -p … -e … -v … imagen` por cada uno |
| 7 | **Respeta el orden**: espera a que la base RESPONDA antes de encender la API | No tiene equivalente: habría que mirarlo a ojo |

Y todo eso **es repetible**: quien lo corra mañana en otro computador obtiene
exactamente lo mismo, porque la secuencia no está en la cabeza de nadie sino
escrita en dos archivos — el `docker-compose.yml` y los `Dockerfile`.

---

### Lo mismo, pero escrito a mano

**Sin compose**, para levantar este proyecto —que tiene **10 servicios**— hay
que escribir esto, en este orden, cada vez:

```powershell
# 1. Crear la red, para que los contenedores se encuentren por su nombre
docker network create proyecto_construccion1_default

# 2. Construir la imagen de front y encenderla
docker build -t front ./front_flask
docker run -d --name front --network proyecto_construccion1_default --restart unless-stopped `
  -e "API_GENERICA_URL=http://api-generica:8011" `
  -e "API_FACTURAS_URL=http://api-facturas:8012" `
  -v "${PWD}/front_flask:/app" `
  -v .:/workspace:cached `
  -p 8010:8010 front flask --app app run --host 0.0.0.0 --port 8010 --debug

# 3. Construir la imagen de api-generica y encenderla
docker build -t api-generica ./api_generica
docker run -d --name api-generica --network proyecto_construccion1_default --restart unless-stopped `
  -e "DB_PROVIDER=${DB_PROVIDER:-postgres}" `
  -e "DB_POSTGRES=postgresql+asyncpg://paradigmas:paradigmas123@postgres:5432/bdfacturas_postgres_local" `
  -e "DB_MARIADB=mysql+aiomysql://paradigmas:paradigmas123@mariadb:3306/bdfacturas_mariadb_local" `
  -e "DB_MYSQL=mysql+aiomysql://paradigmas:paradigmas123@mariadb:3306/bdfacturas_mariadb_local" `
  -e "DB_SQLSERVER=mssql+aioodbc://sa:Paradigmas123!@sqlserver:1433/bdfacturas_sqlserver_local?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes" `
  -v "${PWD}/api_generica:/app" `
  -p 8011:8011 api-generica uvicorn main:app --host 0.0.0.0 --port 8011 --reload

# 4. Construir la imagen de api-facturas y encenderla
docker build -t api-facturas ./api_facturas
docker run -d --name api-facturas --network proyecto_construccion1_default --restart unless-stopped `
  -e "DB_PROVIDER=${DB_PROVIDER:-postgres}" `
  -e "DB_POSTGRES=postgresql+asyncpg://paradigmas:paradigmas123@postgres:5432/bdfacturas_postgres_local" `
  -e "DB_MARIADB=mysql+aiomysql://paradigmas:paradigmas123@mariadb:3306/bdfacturas_mariadb_local" `
  -e "DB_MYSQL=mysql+aiomysql://paradigmas:paradigmas123@mariadb:3306/bdfacturas_mariadb_local" `
  -e "DB_SQLSERVER=mssql+aioodbc://sa:Paradigmas123!@sqlserver:1433/bdfacturas_sqlserver_local?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes" `
  -v "${PWD}/api_facturas:/app" `
  -p 8012:8012 api-facturas uvicorn main:app --host 0.0.0.0 --port 8012 --reload

# 5. Construir la imagen de api-generica-csharp y encenderla
docker build -t api-generica-csharp ./api_generica_csharp
docker run -d --name api-generica-csharp --network proyecto_construccion1_default --restart unless-stopped `
  -e "DatabaseProvider=${DB_PROVIDER:-postgres}" `
  -e "ConnectionStrings__Postgres=Host=postgres;Port=5432;Database=bdfacturas_postgres_local;Username=paradigmas;Password=paradigmas123;Pooling=true;Maximum Pool Size=100;" `
  -e "ConnectionStrings__MariaDB=Server=mariadb;Port=3306;Database=bdfacturas_mariadb_local;Uid=paradigmas;Pwd=paradigmas123;Allow User Variables=true;CharSet=utf8mb4;" `
  -e "ConnectionStrings__SqlServer=Server=sqlserver,1433;Database=bdfacturas_sqlserver_local;User Id=sa;Password=Paradigmas123!;TrustServerCertificate=True;" `
  -v "${PWD}/api_generica_csharp:/app" `
  -v /app/bin `
  -v /app/obj `
  -p 8013:8013 api-generica-csharp

# 6. Construir la imagen de front-blazor y encenderla
docker build -t front-blazor ./front_blazor
docker run -d --name front-blazor --network proyecto_construccion1_default --restart unless-stopped `
  -e "ApiBaseUrl=http://api-generica-csharp:8013" `
  -e "Smtp__User=${SMTP_USER:-}" `
  -e "Smtp__Pass=${SMTP_PASS:-}" `
  -e "Smtp__From=${SMTP_USER:-}" `
  -v "${PWD}/front_blazor:/app" `
  -v /app/bin `
  -v /app/obj `
  -p 8014:8014 front-blazor

# 7. postgres
docker run -d --name postgres --network proyecto_construccion1_default --restart unless-stopped `
  -e "POSTGRES_DB=bdfacturas_postgres_local" `
  -e "POSTGRES_USER=paradigmas" `
  -e "POSTGRES_PASSWORD=paradigmas123" `
  -v pgdata:/var/lib/postgresql/data `
  -v "${PWD}/db/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro" `
  -p 15448:5432 postgres:16-alpine

# 8. ESPERAR a que responda de verdad… mirándolo a ojo

# 9. mariadb
docker run -d --name mariadb --network proyecto_construccion1_default --restart unless-stopped `
  -e "MARIADB_ROOT_PASSWORD=paradigmas123" `
  -e "MARIADB_DATABASE=bdfacturas_mariadb_local" `
  -e "MARIADB_USER=paradigmas" `
  -e "MARIADB_PASSWORD=paradigmas123" `
  -v mariadbdata:/var/lib/mysql `
  -v "${PWD}/db/mariadb/init.sql:/docker-entrypoint-initdb.d/init.sql:ro" `
  -p 13316:3306 mariadb:11

# 10. ESPERAR a que responda de verdad… mirándolo a ojo

# 11. phpmyadmin
docker run -d --name phpmyadmin --network proyecto_construccion1_default --restart unless-stopped `
  -e "PMA_HOST=mariadb" `
  -e "PMA_USER=paradigmas" `
  -e "PMA_PASSWORD=paradigmas123" `
  -p 8091:80 phpmyadmin:latest

# 12. sqlserver
docker run -d --name sqlserver --network proyecto_construccion1_default --restart unless-stopped `
  -e "ACCEPT_EULA=Y" `
  -e "MSSQL_SA_PASSWORD=Paradigmas123!" `
  -e "MSSQL_PID=Developer" `
  -v mssqldata:/var/opt/mssql `
  -p 11443:1433 mcr.microsoft.com/mssql/server:2022-latest

# 13. ESPERAR a que responda de verdad… mirándolo a ojo

# 14. sqlserver-init
docker run -d --name sqlserver-init --network proyecto_construccion1_default --restart no --entrypoint /bin/bash `
  -e "MSSQL_SA_PASSWORD=Paradigmas123!" `
  -v "${PWD}/db/sqlserver:/scripts:ro" mcr.microsoft.com/mssql/server:2022-latest /scripts/init.sh

```

**16 comandos**, con sus flags, en un orden que no se puede equivocar.
Con compose, todo eso es:

```powershell
docker compose up -d --build
```

**De dónde sale cada pedazo:**

| Lo que antes era un flag | Ahora vive en |
|---|---|
| `docker build -t … ./carpeta` | `build:` del compose, y el **`Dockerfile`** de esa carpeta dice cómo |
| `-p 8080:8080` | `ports:` |
| `-e VARIABLE=valor` | `environment:` |
| `-v origen:destino` | `volumes:` |
| `--network …` | Compose la crea sola y mete a todos adentro |
| `--name` | El nombre del servicio |
| El orden y la espera | `depends_on:` + `healthcheck:` |

Y las dos banderas del comando:

| Bandera | Qué hace | Cuándo se usa |
|---|---|---|
| `-d` | Lo deja corriendo **en segundo plano** y le devuelve la terminal | Casi siempre. Sin ella la terminal queda pegada |
| `--build` | **Reconstruye** las imágenes propias antes de encender | La primera vez, y cada vez que cambie un `Dockerfile` |

> **Por eso el curso dice «un solo comando».** No es comodidad: es que el
> sistema entero queda **escrito** en dos archivos en vez de vivir en la
> memoria de quien lo levantó la primera vez. Cualquiera lo reproduce igual,
> y eso es lo que hace que su proyecto sea entregable.


## 6. Kubernetes (y por qué este curso NO lo necesita)

Kubernetes (K8s) es el orquestador de contenedores **a escala de clúster**:
reparte contenedores entre muchas máquinas, escala réplicas según demanda,
reprograma lo que se cae y hace despliegues sin downtime. Compose y K8s no
compiten: Compose orquesta **en una máquina**; K8s orquesta **un clúster**.

| Kubernetes resuelve… | ¿Existe ese problema aquí? |
|---|---|
| Repartir contenedores entre muchas máquinas | No — los 10 corren en su PC |
| Escalar a N réplicas cuando sube el tráfico | No — el "tráfico" es usted con el navegador |
| Alta disponibilidad (un nodo muere → reprogramar) | No — si su PC se apaga, se acabó la clase |
| Despliegue continuo sin caída (rolling updates) | No — "actualizar" es guardar y que recargue |
| Secretos, RBAC, múltiples equipos | No — credenciales didácticas, un usuario |

Y su precio es alto: plano de control (API server, etcd, scheduler),
manifiestos YAML mucho más extensos, y conceptos nuevos (pods, ingress,
namespaces) que taparían lo que este curso sí enseña.

**La regla profesional:** Compose para desarrollo local y sistemas de un
host; Kubernetes cuando se necesita más de una máquina, réplicas elásticas o
sobrevivir a la caída de un nodo. **El puente conceptual:** ambos son YAML
declarativo describiendo estado deseado — quien domina un compose ya entiende
la mitad conceptual de K8s; le falta solo la parte de clúster.

## 7. Los comandos que este curso usa (chuleta)

```powershell
docker ps                        # qué está corriendo (con -a: también lo detenido)
docker stop X / docker start X   # apagar / encender (los datos se conservan)
docker logs X                    # ver la salida del contenedor (errores incluidos)
docker exec X comando            # ejecutar algo DENTRO del contenedor
# … y los de todos los días en este proyecto:
docker compose up -d --build     # materializar el docker-compose.yml (con rebuild)
DB_PROVIDER=mariadb docker compose up -d   # las 3 APIs cambian de motor sin tocar código
docker compose ps                # estado de los servicios del compose
docker compose logs api-generica # la salida de un servicio (errores incluidos)
docker compose down [-v]         # apagar todo (-v: borrar también los volúmenes = reset BD)
docker compose up -d --remove-orphans  # además, borrar contenedores huérfanos (sección 5)
```

### Cómo se leen los comandos que encuentre por ahí

Fíjese en la `X` de arriba: **no es parte del comando**. Está puesta donde va
un valor suyo — el nombre de su contenedor. Y el `[-v]` va entre corchetes
cuadrados porque es **opcional**.

Esa forma de escribir no es de este documento: es la de toda la
documentación técnica. En la página de Docker, en la de Git y en cualquier
respuesta de internet va a encontrar comandos así:

```
docker stop <nombre>
docker logs <contenedor>
git clone <url>
```

**Los signos `<` y `>` NO se escriben.** Son una marca que quiere decir
*«aquí va un valor suyo»*, y lo de adentro dice qué clase de valor.

**Ejemplo completo.** La documentación dice:

```
docker stop <nombre>
```

Usted primero averigua el nombre:

```powershell
docker ps
```

```
NAMES                              PORTS
proyecto_php1-api-facturas-1       0.0.0.0:8022->8022/tcp
proyecto_php1-mariadb-1            0.0.0.0:13326->3306/tcp
```

Y después escribe **el nombre tal como aparece**, sin los signos:

```powershell
docker stop proyecto_php1-api-facturas-1
```

Lo que **no** se escribe:

| Mal | Por qué |
|---|---|
| `docker stop <nombre>` | Dejó la marca en vez de reemplazarla |
| `docker stop <proyecto_php1-api-facturas-1>` | Puso el valor, pero dejó los signos |
| `docker stop "proyecto_php1-api-facturas-1"` | Las comillas sobran aquí |

**Las tres marcas que verá siempre:**

| Marca | Significa |
|---|---|
| `<algo>` | Obligatorio. Reemplácelo por su valor, sin los signos |
| `[algo]` | Opcional. Puede omitirlo entero |
| `a\|b` | Escoja uno de los dos |

**¿Y de dónde sale el valor?** Casi siempre de un comando que lista lo que
hay: para contenedores es `docker ps`, y el nombre está en la columna
`NAMES`.


## 8. ¿Hace falta una cuenta de Docker?

**No.** Las imágenes que usa este proyecto son **públicas**: se descargan sin
registrarse, sin iniciar sesión y sin pagar nada.

Al abrir Docker Desktop puede aparecer una ventana pidiendo *Sign in* o
*Create an account*. **Ciérrela, o escoja «Continue without signing in».**
Todo funciona igual.

### ¿Y si ya tiene cuenta y entra con ella?

**También funciona**, y hasta ayuda un poco: Docker Hub le da un límite de
descargas más alto a quien tiene la sesión abierta que a quien descarga de
forma anónima.

Dicho eso, **para este proyecto no hace falta**: ni para descargar las
imágenes, ni para levantarlas, ni para trabajar.

### Lo único que sí es obligatorio

**Que Docker Desktop esté encendido.** Ábralo y espere a que termine de
arrancar: el icono de la ballena, abajo a la derecha, deja de moverse.

Si Docker está apagado, cualquier comando responde algo así:

```
error during connect: ... the docker daemon is not running
```

Ese mensaje **no es un problema del proyecto**: es Docker que no está
corriendo. Enciéndalo y repita el comando.

---

## 9. Referencias

1. Docker — *Docker overview* (documentación oficial):
   <https://docs.docker.com/get-started/docker-overview/>
2. Docker — conceptos de imágenes y contenedores:
   <https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/>
3. Docker — volúmenes y almacenamiento:
   <https://docs.docker.com/engine/storage/volumes/>
4. Docker Compose — documentación oficial:
   <https://docs.docker.com/compose/>
5. Kubernetes — *Overview* (documentación oficial):
   <https://kubernetes.io/es/docs/concepts/overview/>
6. En este repositorio: el `docker-compose.yml` de la raíz (10 servicios) y
   el diagrama de contenedores del [README](../README.md).
