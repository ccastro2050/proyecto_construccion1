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

## 8. Referencias

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
