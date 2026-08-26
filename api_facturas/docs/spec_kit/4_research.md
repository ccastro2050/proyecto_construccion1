# Investigación y decisiones — API Facturas

> **Documento 4 de 8** del spec kit · **Lectura opcional** (contexto de por qué
> el plan es como es; se puede saltar directo a 5_data_model.md si solo se va a
> construir). Registra cada decisión técnica, las alternativas consideradas y
> su justificación.

---

## D1 — FastAPI en vez de Flask/Django REST
**Decisión:** FastAPI. **Por qué:** async nativo, Swagger automático (clave para
que los estudiantes "vean" la API), y la validación Pydantic es exactamente el
concepto que esta API enseña. Flask exigiría armar a mano lo que FastAPI ya
trae (validación, docs); Django trae demasiada magia para un curso de arquitectura.

## D2 — SQL a mano con `text()` en vez de ORM declarativo
**Decisión:** SQLAlchemy async solo como ejecutor (`text()` + parámetros
nombrados), sin modelos ORM. **Alternativas:** ORM declarativo (oculta el SQL,
que es justo lo que el curso quiere mostrar), drivers crudos por motor (tres
paramstyles distintos: `%s`, `?`, `$1` — ruido didáctico). Con `text()` el mismo
`:param` funciona en los 3 motores y el SQL queda visible y comparable.

## D3 — Interfaces con `typing.Protocol` en vez de ABC
**Decisión:** `Protocol` (tipado estructural: cumplir el contrato sin heredar).
**Por qué:** muestra la D de SOLID sin acoplar por herencia; una clase con los
métodos correctos "es" un repositorio. El costo es que el incumplimiento se
detecta por type-checker/en runtime al llamar, no al instanciar — aceptable en
contexto docente.

## D4 — Clases base por motor + repositorios delgados por entidad
**Decisión:** todo el SQL de un dialecto vive en `BaseRepositorio<Motor>` con 6
operaciones parametrizadas por nombre de tabla; el repositorio de entidad son
~35 líneas de constantes + delegación. **Alternativa rechazada:** SQL escrito a
mano en cada uno de los 36 repositorios (36 × ~200 líneas casi duplicadas).
**Trade-off aceptado:** los repos de entidad quedan tan delgados que casi no
"se ve" el SQL en ellos — por eso el DDL de referencia y el corte vertical de
persona se documentan aparte.

## D5 — Detección de tipos vía `information_schema`
**Problema:** los valores de PK llegan como texto por la URL (`/api/cliente/5`),
pero la columna es INTEGER. **Decisión:** consultar
`information_schema.columns` y convertir (`_detectar_tipo_columna` +
`_convertir_valor`). **Alternativa rechazada:** exigir el tipo correcto al
cliente (complica a todos los consumidores y rompe la uniformidad de las URLs).
**Costo:** una consulta extra de catálogo por operación con clave.

## D6 — La lógica de facturación en la BD, no en Python
**Decisión:** el trigger `actualizar_totales_y_stock` y los SP hacen los
cálculos. La API inserta renglones "crudos" (`subtotal: 0`) y la BD corrige.
**Por qué:** el curso enseña ACID y lógica en BD; además garantiza consistencia
sin importar qué API (o cliente SQL) escriba. **Consecuencia:** no hay endpoint
"crear factura con detalle" — eso es de los SP.

## D7 — Sin `RETURNING` / `OUTPUT INSERTED`
**Decisión original:** `crear()` devuelve `bool` (rowcount > 0); el POST no
devuelve la PK generada en entidades SERIAL. **Por qué se mantuvo:** simetría
entre los 3 dialectos con el mínimo SQL. **Mejora opcional documentada:** añadir
`RETURNING`/`OUTPUT`/`LAST_INSERT_ID()` por dialecto si un consumidor necesita el id.

## D8 — BCrypt directo con costo 12
**Decisión:** `bcrypt.gensalt(rounds=12)` + `hashpw`/`checkpw`, funciones puras
`encriptar`/`verificar` (esta última devuelve `False` ante cualquier excepción:
un hash corrupto no tumba el login). `passlib` queda declarado por
compatibilidad pero no se usa. La encriptación se dispara por la constante
`CAMPOS_ENCRIPTAR` del repositorio (usuario) o por query param en el genérico.

## D9 — Fábrica por función + diccionario, sin `Depends`
**Decisión:** `crear_servicio_<entidad>()` llamada dentro de cada handler.
**Alternativa:** inyección con `Depends` de FastAPI — más idiomática pero
introduce un concepto extra; el curso prioriza ver el patrón Factory "a pelo".
**Deuda conocida:** se crea un `AsyncEngine` por petición (el caché es por
instancia de repo). Mejora opcional: cachear engine por proveedor a nivel de módulo.

## D10 — Orden de registro de routers
`entidades_controller` declara `GET /api/{tabla}`: si se registrara primero,
capturaría TODAS las rutas `/api/*`. FastAPI resuelve por orden de registro →
los 12 específicos van primero, el genérico de último. Esto es un requisito,
no un estilo.

## D11 — Hallazgos del código original (elegir al reconstruir)
1. **Controller genérico roto (CORREGIDO, agosto de 2026):** `ServicioCrud`
   llama `obtener_filas(...)` pero las bases solo exponían
   `_obtener_filas(...)` → 500. Resuelto en
   `repositorios/repositorio_lectura_generico.py`: las clases
   `RepositorioLectura*` ahora exponen las 6 operaciones públicas del
   contrato delegando en los métodos protegidos de las bases.
2. **DELETE de PK compuesta filtra solo el primer segmento** en las 3 tablas
   puente → borra de más. *Recomendación:* corregir (WHERE por ambas columnas)
   y anotarlo; réplica fiel solo si se quiere estudiar el bug.
3. **Sin CORS:** los consumidores originales llamaban del lado servidor, por
   eso nunca dolió. *Recomendación:* añadir `CORSMiddleware` abierto.
4. **`SELECT TOP ({n})` interpolado** en SQL Server: validar que `limite` sea
   entero antes de interpolar.
5. **`lru_cache` en `get_settings()`:** cambiar `DB_PROVIDER` exige reiniciar
   el proceso — aceptado y documentado.
