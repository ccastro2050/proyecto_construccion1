# Investigación y decisiones — Frontend Flask

> **Documento 4 de 8** del spec kit · **Lectura opcional** (contexto de por qué
> el plan es como es). Cada decisión con sus alternativas y justificación.

---

## D1 — Flask server-side en vez de SPA (React/Vue)
**Decisión:** HTML renderizado en servidor con Jinja2, cero JavaScript propio.
**Por qué:** el curso enseña la SEPARACIÓN de capas, no frontend moderno; con
formularios clásicos el flujo petición→respuesta es visible y depurable. Una SPA
introduciría build tools, estado en cliente y CORS — ruido para el objetivo.
**Consecuencia:** las APIs se consumen del lado servidor, por eso no necesitan
CORS para este front.

## D2 — `requests` síncrono en vez de `httpx` async
Flask es síncrono por defecto; `requests` es la librería que los estudiantes
verán en cualquier tutorial. Async no aporta nada con una petición por vista
(la única pantalla con 2 llamadas secuenciales es inicio, y esa lentitud es
tolerable y didáctica).

## D3 — Una clase `ClienteApi` en vez de `requests` en las rutas
**Decisión:** todo HTTP en `servicios/cliente_api.py`, contrato
`(exito, resultado)`. **Por qué:** (a) es la misma idea de "capa de servicio"
que las APIs enseñan del otro lado; (b) permite cambiar de API activa en un solo
lugar; (c) las rutas quedan lineales: llamar → flash → render/redirect.
El cliente **nunca lanza**: convierte `RequestException` en mensajes legibles,
extrayendo el `detail.detalle`/`detail.mensaje` de FastAPI para que un error de
llave foránea de la BD llegue textual hasta la alerta del navegador.

## D4 — Selector de API en `session` (cookie firmada)
**Alternativas:** query param en cada URL (contamina todos los enlaces),
cookie manual (reinventa lo que Flask ya da), variable global (rompe con
múltiples usuarios). **Decisión:** `session["api"]` con whitelist
`("generica", "facturas")` + un context processor que inyecta `api_activa` en
todas las plantillas. Redirect a `request.referrer` para volver a la página
donde se hizo clic.

## D5 — La diferencia entre APIs, encapsulada en dos helpers
La API Genérica necesita el nombre de la columna clave
(`/api/{tabla}/{clave}/{valor}`) y la de Facturas ya conoce su PK
(`/api/{tabla}/{valor}`, colección con barra final). **Decisión:** `_url_listar`
y `_url_registro` absorben TODA la diferencia; el resto del front es idéntico
para ambas. Esto ES la tesis del proyecto: el front no depende del backend.

## D6 — Bootstrap por CDN, CSS propio de 3 reglas
Cero build step, cero npm. El costo (requiere internet la primera carga) es
aceptable en aula. El CSS propio se limita a lo que Bootstrap no da: hover de
las tarjetas de inicio y encabezados de tabla en versalitas.

## D7 — Facturas de solo lectura, detalle filtrado en Python
Crear/editar facturas toca stock, subtotales y totales — lógica que vive en la
BD (triggers/SP). **Decisión:** el front solo lista y muestra. El detalle trae
`productosporfactura` COMPLETO y filtra en Python (`fknumfactura == numero`):
ineficiencia **deliberada y comentada** para contrastar con un `WHERE` de SQL
en clase. A escala real: filtro en la API.

## D8 — Formularios: PK deshabilitada en edición
El input de la clave va `disabled` al editar (no viaja en el POST) y la ruta lo
toma del path. Enseña que la PK no se actualiza y evita ediciones inconsistentes.
Validación en el navegador por atributos HTML (`required`, `maxlength`,
`type=email/number`, `min`, `step`); la validación fuerte es del backend.

## D9 — Brechas aceptadas (documentadas, no accidentales)
Sin páginas 404/500 propias; sin repoblado del formulario si falla un POST de
creación; `int()`/`float()` del form sin try/except (mitigado por
`type="number"`); URLs de Swagger de la página de inicio hardcodeadas a
localhost; sin paginación/búsqueda; `SECRET_KEY` con default de desarrollo.
Cada una es una simplificación consciente para mantener el código corto; se
listan en [2_spec.md](2_spec.md) §6 para que quien reconstruya decida.
