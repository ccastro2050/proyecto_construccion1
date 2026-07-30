# Investigación y decisiones — API Genérica CRUD

> **Documento 4 de 8** del spec kit · **Lectura opcional** (contexto de por qué
> el plan es como es). Cada decisión con sus alternativas y justificación.

---

## D1 — ¿Por qué una API "genérica"?
**Decisión:** endpoints parametrizados por nombre de tabla (`/api/{tabla}`).
**Por qué:** demuestra que un CRUD es una operación uniforme; una sola
implementación sirve para las 12 tablas de la BD de prueba (y cualquier otra).
**Precio asumido:** sin validación por entidad (un body con campos inventados
llega hasta la BD y falla allá) y superficie genérica difícil de asegurar —
aceptable en contexto docente, inaceptable en producción sin allowlist de tablas.

## D2 — FastAPI + SQLAlchemy async con `text()`
Mismas razones que en cualquier API del proyecto: Swagger automático, async
nativo. `text()` + parámetros nombrados `:x` unifica el paramstyle de los 3
drivers (asyncpg usa `$1`, aioodbc usa `?`, aiomysql usa `%s` — SQLAlchemy los
traduce). ORM declarativo descartado: exige modelos por tabla, lo contrario de
la genericidad.

## D3 — Descubrimiento de tipos vía `information_schema`
**Problema:** todo llega como texto por la URL (`/api/factura/numero/1`), pero
`numero` es INTEGER, `fecha` es TIMESTAMP, etc. **Decisión:**
`_detectar_tipo_columna()` consulta el catálogo estándar
`information_schema.columns` (existe en los 3 motores) y `_convertir_valor()`
convierte a `int`/`Decimal`/`float`/`bool`/`UUID`/`date`/`datetime`/`time`.
**Caso especial resuelto:** buscar `2025-12-03` en una columna TIMESTAMP compara
solo la fecha (`CAST(col AS DATE)`). **Alternativa rechazada:** exigir tipos al
cliente (rompería el frontend genérico del proyecto padre).

## D4 — Un repositorio por dialecto, misma interfaz
Las diferencias reales entre motores son pocas y localizadas: comillas de
identificador (`"` / `` ` `` / `[]`), LIMIT vs TOP, y el esquema por defecto
(`public` / ninguno / `dbo`). **Decisión:** 3 clases con los mismos 6 métodos
(`IRepositorioLecturaTabla` como Protocol) y la fábrica elige por diccionario.
Agregar un motor = 1 clase + 1 línea (principio abierto/cerrado).

## D5 — Interfaces con `typing.Protocol` en vez de ABC
Tipado estructural: cumplir el contrato sin heredar. Muestra inversión de
dependencias sin acoplamiento por herencia; el servicio recibe "algo que tenga
estos 6 métodos".

## D6 — Encriptación como responsabilidad del repositorio
`campos_encriptar` (CSV por query param) se aplica en `crear`/`actualizar`
dentro del repositorio, justo antes del SQL. **Por qué ahí y no en el
servicio:** el hash es parte de "cómo se persiste", y así el servicio queda
igual para todos los motores. `verificar()` sí vive en el servicio (es regla de
negocio: 200/401/404).

## D7 — bcrypt directo, costo 12
`bcrypt.gensalt(rounds=12)` + `hashpw`/`checkpw`. `verificar()` devuelve `False`
ante cualquier excepción (hash malformado ≠ crash). `passlib` declarado en
requirements por compatibilidad histórica, sin uso directo.

## D8 — Envoltura de respuesta propia en vez de listas crudas
`{tabla, esquema, total, datos}` en vez de `[...]`. **Por qué:** el estudiante
ve metadatos del contexto (qué tabla, cuántas filas) y los errores tienen forma
uniforme `{estado, mensaje, detalle}`. 204 para tabla vacía enseña la semántica
HTTP "éxito sin contenido".

## D9 — Engine perezoso por instancia de repositorio
`create_async_engine` se crea en el primer uso y se cachea en la instancia.
Como la fábrica crea un repositorio por petición, en la práctica hay un engine
por petición. **Deuda conocida y aceptada** (pool efectivo nulo); mejora
opcional: cachear el engine por proveedor a nivel de módulo.

## D10 — `lru_cache` en `get_settings()`
La configuración se lee una vez por proceso: cambiar `DB_PROVIDER` exige
reiniciar. A cambio, ninguna operación relee `.env`. En Docker esto es
irrelevante (las variables llegan al arrancar el contenedor).

## D11 — Swagger en `/swagger` en vez de `/docs`
Herencia deliberada del proyecto C# original (ASP.NET publica en `/swagger`).
Mantiene familiaridad para quien viene de ese stack y diferencia esta API de la
API de Facturas (que usa el `/docs` default) en el proyecto padre.
