# Constitución — Frontend Flask

> **Documento 1 de 8** del spec kit. Orden de lectura:
> `1_constitution → 2_spec → 3_plan → 4_research → 5_data_model → 6_contracts → 7_quickstart → 8_tasks`.
>
> Principios innegociables de ESTE proyecto tratado como independiente. Si se
> construye dentro del proyecto padre (proyecto_construccion1), aplica además la
> constitución global en `docs/spec_kit/1_constitution.md` de la raíz.

---

## Artículo 1 — Propósito didáctico

Frontend para enseñar la capa de presentación de una arquitectura de 3 capas
con el mínimo de tecnología: Flask + Jinja2 + Bootstrap, sin JavaScript propio.
Claridad sobre sofisticación:

- Todo en **español**: código, comentarios, plantillas, mensajes al usuario.
- Cada archivo abre con un docstring que explica su papel y los conceptos que
  ilustra (bloques "CONCEPTO — …"); las plantillas también van comentadas (`{# #}`).
- Trato de **usted** al lector y "invitaciones a experimentar" en la propia UI.

## Artículo 2 — El front NUNCA toca la base de datos

- Cero drivers de BD, cero SQL. Solo dos dependencias: `flask` y `requests`.
- Todo dato entra y sale por HTTP contra las APIs (Genérica :8001 / Facturas :8002).
- Todo `requests` vive en UNA clase (`ClienteApi`); las rutas jamás llaman HTTP directo.

## Artículo 3 — Independencia del backend

El usuario cambia la **API activa** (Genérica ↔ Facturas) en caliente y TODAS
las pantallas siguen funcionando igual. Ninguna vista puede depender de rasgos
de una API concreta; la única diferencia permitida (formato de URL) se encapsula
en dos helpers privados del cliente HTTP.

## Artículo 4 — Patrones de interacción fijos

- **Formularios web clásicos** sin JavaScript: GET muestra, POST procesa.
- **Post→Redirect→Get** tras toda escritura, con mensaje **flash**
  (solo categorías `success` y `danger`, que mapean a alertas Bootstrap).
- **Eliminar SIEMPRE por POST** (nunca un enlace GET), con `confirm()` inline.
- **Degradación elegante**: API caída = flash con el error + página vacía
  navegable; nunca un traceback al usuario.
- Contrato interno del cliente HTTP: `(exito: bool, resultado)` — el cliente
  nunca lanza; la ruta decide qué mostrar.

## Artículo 5 — Los cálculos viven en el backend

El front **formatea, no calcula**: totales y subtotales de facturas llegan ya
calculados (los produce la BD del sistema). Prohibido sumar/multiplicar montos
en Python o Jinja; solo formato de presentación (`$ {:,.0f}`, fechas recortadas).

## Artículo 6 — Convenciones fijas

| Cosa | Convención |
|---|---|
| Puerto | **8000** (`flask run --port 8000`, `--debug` en desarrollo) |
| Estilos | Bootstrap 5.3 + Bootstrap Icons por CDN; CSS propio mínimo (~3 reglas) |
| Blueprints | variable `bp_<nombre>`, nombre interno sin prefijo, `url_prefix` propio |
| Plantillas | `<entidad>_<vista>.html`; herencia de `base.html`; bloques `titulo`/`contenido` |
| Estado de sesión | solo la clave `"api"` (`"generica"` \| `"facturas"`), default `"generica"` |
| Configuración | `API_GENERICA_URL`, `API_FACTURAS_URL`, `SECRET_KEY` por variables de entorno |
