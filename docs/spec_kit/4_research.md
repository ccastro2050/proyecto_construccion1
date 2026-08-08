# Investigación y decisiones — Infraestructura e integración

> **Documento 4 de 8** del spec kit raíz · **Lectura opcional** (contexto de por
> qué el plan es como es).

---

## D1 — Docker Compose para TODO, incluso las BD
**Alternativas:** motores instalados en cada PC de estudiante (heterogéneo,
imposible de soportar), una sola BD compartida en la nube (sin trabajo offline,
un punto de falla para todo el curso). **Decisión:** todo en contenedores; el
único requisito es Docker Desktop. La primera descarga es grande UNA vez; después
arranca en segundos.

## D2 — Tres motores con la MISMA base de datos
El objetivo del curso es demostrar independencia del motor. Tener PostgreSQL,
MariaDB y SQL Server simultáneos, con idénticas tablas/datos/triggers/SP en su
dialecto, permite cambiar `DB_PROVIDER` y comparar en vivo. **Costo aceptado:**
mantener 3 scripts SQL equivalentes a mano.

## D3 — Puertos de BD desplazados (15442/13316/11443)
Muchos estudiantes ya tienen PostgreSQL/MySQL/SQL Server locales en los puertos
estándar. Publicar 5432/3306/1433 chocaría. Dentro de la red de compose se usan
los estándar (los contenedores no chocan entre sí).

## D4 — `sqlserver-init` como contenedor efímero
Postgres y MariaDB ejecutan `/docker-entrypoint-initdb.d` con volumen vacío; la
imagen de SQL Server NO tiene ese mecanismo. **Decisión:** un servicio auxiliar
con la misma imagen (trae `sqlcmd`), `depends_on: service_healthy`, que verifica
en `sys.databases` si la BD existe y solo entonces crea + puebla. `restart: "no"`:
corre y muere. **Alternativa rechazada:** script dentro del mismo contenedor
sqlserver con `&` (frágil, mezcla responsabilidades).

## D5 — Sin `depends_on` de las apps hacia las BD
Las APIs crean su engine de forma perezosa (primera petición), así que toleran
que la BD tarde. Quitar la dependencia acelera el arranque y evita el problema
clásico de "healthy pero aún cargando datos". El front tolera APIs caídas por
diseño (badges rojos).

## D6 — Código montado como volumen + reload
`./front_flask:/app` etc. + `--debug`/`--reload`: guardar un archivo recarga la
app sin rebuild. Rebuild (`--build`) solo cuando cambian dependencias o
Dockerfiles. Es la diferencia entre iterar en 2 segundos o en 2 minutos de clase.

## D7 — `DB_PROVIDER` con interpolación `${DB_PROVIDER:-postgres}`
El motor por defecto es PostgreSQL (el más liviano y estándar de los 3); la
variable del shell del host lo sobreescribe sin editar archivos:
`$env:DB_PROVIDER = "mariadb"; docker compose up -d`.

## D8 — phpMyAdmin con auto-login
`PMA_USER`/`PMA_PASSWORD` fijos: los estudiantes entran a http://localhost:8091
sin pantalla de credenciales. Riesgo nulo: entorno local docente. Solo cubre
MariaDB; para los otros motores están SQLTools (devcontainer) y las herramientas
del host.

## D9 — Devcontainer adosado al servicio `front`
Reutiliza un contenedor que ya corre (no crea otro), y por eso `front` monta el
repo completo en `/workspace`. SQLTools se conecta con los **hosts internos**
(`postgres:5432`…) porque VS Code queda DENTRO de la red de compose.

## D10 — Volúmenes nombrados y `down -v` como reset oficial
Los datos sobreviven a `down` y reinicios (aprendizaje de persistencia). El
"botón de pánico" documentado es `down -v` + `up -d`: los init.sql solo corren
sobre volumen vacío, así que también es la vía para aplicar cambios de esquema.

## D11 — Credenciales públicas a propósito
`paradigmas/paradigmas123` y `sa/Paradigmas123!` están en el repo deliberadamente:
son didácticas y el entorno jamás va a producción. La de SQL Server cumple su
política de complejidad mínima.
