# Especificación — Frontend Flask

> **Documento 2 de 8** de un spec kit **autocontenido**: con esta carpeta se
> reconstruye el frontend completo desde cero, como proyecto independiente.
>
> | # | Documento | Contenido |
> |---|---|---|
> | 1 | [1_constitution.md](1_constitution.md) | Principios innegociables |
> | 2 | **2_spec.md** (este) | QUÉ construir: requisitos y criterios de aceptación |
> | 3 | [3_plan.md](3_plan.md) | CÓMO: stack, estructura, piezas clave |
> | 4 | [4_research.md](4_research.md) | Decisiones técnicas y alternativas *(lectura opcional)* |
> | 5 | [5_data_model.md](5_data_model.md) | Datos por pantalla y estado de sesión *(informativo: no hay BD propia)* |
> | 6 | [6_contracts.md](6_contracts.md) | Rutas propias + endpoints que consume de las APIs |
> | 7 | [7_quickstart.md](7_quickstart.md) | Arranque y recorrido de validación |
> | 8 | [8_tasks.md](8_tasks.md) | Orden de construcción por fases verificables |

---

## 1. Propósito

Construir la **capa de presentación** de la arquitectura de 3 capas: una
aplicación Flask que renderiza HTML con Bootstrap y consume por HTTP las dos
APIs del proyecto (Genérica en :8001 y Facturas en :8002). El front **nunca**
toca la base de datos: no importa drivers, solo hace peticiones HTTP.

Objetivo pedagógico central: el usuario puede **cambiar de API activa en
caliente** (Genérica ↔ Facturas) y todas las pantallas siguen funcionando igual
— demostración de que el front no depende de cómo está construido el backend.

## 2. Alcance

**Incluye:** página de inicio con estado de las APIs, CRUD completo de productos
y de personas, vista de facturas (lista + detalle maestro-detalle, solo lectura),
explorador de las 12 tablas, selector de API activa.

**No incluye:** JavaScript propio (solo Bootstrap y dos atributos inline),
autenticación/login, creación o edición de facturas (los totales/stock los
maneja la BD con triggers y SP), paginación/búsqueda/ordenamiento.

## 3. Requisitos funcionales

### RF1 — Página de inicio (`GET /`)
- Título "Arquitectura de 3 capas" + diagrama ASCII de la arquitectura en un `<pre>`.
- Dos tarjetas (una por API) con **badge de estado**: consulta `GET {api}/`
  con timeout de 5 s; si responde → `en línea` (verde, borde success); si no →
  `sin conexión` (rojo, borde danger).
- Cada tarjeta: descripción del enfoque de esa API, botón a su Swagger
  (`localhost:8001/swagger` y `localhost:8002/swagger`, abren en pestaña nueva)
  y botón "Usar esta API".
- Cierra con una alerta informativa invitando a cambiar de API y comparar.

### RF2 — Selector de API activa (`GET /cambiar-api/<nombre>`)
- La elección vive en la **sesión** de Flask (cookie firmada), clave `"api"`,
  valores válidos `"generica"` | `"facturas"`, default `"generica"`.
- Lista blanca estricta: un valor inválido se ignora en silencio.
- Redirige a la página desde donde se hizo clic (`request.referrer`, con
  fallback al inicio).
- Un *context processor* inyecta `api_activa` en TODAS las plantillas; el navbar
  muestra `API: Genérica|Facturas` en un dropdown con la opción activa marcada.

### RF3 — CRUD de productos (`/productos`) — EL EJEMPLO GUÍA
| Ruta | Método | Comportamiento |
|---|---|---|
| `/productos/` | GET | Tabla: Código, Nombre, Stock, Valor unitario (formato `$ 9,999`), Acciones |
| `/productos/nuevo` | GET/POST | Formulario crear (campos: codigo≤10, nombre≤100, stock≥0, valorunitario≥0 step 0.01) |
| `/productos/editar/<codigo>` | GET/POST | Mismo formulario; `codigo` deshabilitado (viene del path) |
| `/productos/eliminar/<codigo>` | POST | Con `confirm()` JS; flash + redirect |

- Flujo clásico de formularios sin JavaScript: GET muestra, POST procesa,
  y tras escribir siempre **Post→Redirect→Get** con mensaje flash
  (`success` verde / `danger` rojo).
- Si la API falla al listar: flash con el error y tabla vacía (nunca página de error).
- Conversiones en el POST: `stock` → int, `valorunitario` → float, textos con `.strip()`.

### RF4 — CRUD de personas (`/personas`)
Mismo patrón EXACTO que productos (es el ejercicio de replicación) con campos
`codigo`, `nombre`, `email` (input type=email), `telefono` — todos texto.
La lista incluye una alerta didáctica: eliminar una persona usada como
cliente/vendedor falla por llave foránea y el error de la BD se ve en pantalla.

### RF5 — Facturas, solo lectura (`/facturas`)
- Lista: Número, Fecha (solo `YYYY-MM-DD`), Estado (badge: rojo si `anulada`,
  verde si no, texto default `activa`), Total formateado, Cliente (id),
  Vendedor (id), botón "Ver".
- Detalle `/facturas/<int:numero>`: breadcrumb, tarjeta maestro (fecha completa
  `YYYY-MM-DD HH:MM:SS`, estado, cliente, vendedor, total en verde) + tabla de
  renglones (código producto, cantidad, subtotal).
- El detalle se obtiene listando `productosporfactura` completo y **filtrando en
  Python** por `fknumfactura == numero` — ineficiencia deliberada y documentada
  para contrastar con un `WHERE` de SQL.
- El front **no calcula nada**: total y subtotales vienen calculados por los
  triggers de la BD (alerta informativa lo explica).

### RF6 — Explorador de tablas (`/explorador/?tabla=X`)
- `<select>` con las 12 tablas (constante en código, orden fijo:
  empresa, persona, producto, cliente, vendedor, factura, productosporfactura,
  usuario, rol, rol_usuario, ruta, rutarol), auto-submit con `onchange`;
  tabla por defecto: `persona`.
- Columnas **dinámicas**: se deducen de las claves de la primera fila
  (`list(filas[0].keys())`).
- Usa la **API activa** y el encabezado dice con cuál se consultó
  ("Tabla X — N registros (consultados con la API Genérica/Facturas)").

### RF7 — Cliente HTTP único
Toda petición HTTP sale de UNA clase (`ClienteApi`); las rutas jamás usan
`requests` directamente. Contrato: métodos que devuelven `(exito: bool, resultado)`;
la ruta decide el flash. Debe absorber la diferencia entre las dos APIs:

| Operación | API Genérica | API Facturas |
|---|---|---|
| Listar | `GET {base}/api/{tabla}` | `GET {base}/api/{tabla}/` (barra final) |
| Registro | `{base}/api/{tabla}/{clave}/{valor}` | `{base}/api/{tabla}/{valor}` (la API ya conoce su PK) |

Ambas responden el sobre `{"tabla", "total", "datos": [...]}`; el 204 se traduce
a lista vacía. Los errores de FastAPI (`detail.detalle` o `detail.mensaje`) se
extraen y se muestran textuales al usuario — así un error de llave foránea de la
BD llega hasta la alerta del navegador.

## 4. Requisitos no funcionales

- **RNF1 — Solo 2 dependencias:** `flask>=3.0` y `requests>=2.31`.
- **RNF2 — Bootstrap 5.3 + Bootstrap Icons por CDN**; CSS propio mínimo
  (~3 reglas: hover de tarjetas y encabezados de tabla en versalitas).
- **RNF3 — Puerto 8000**, `--debug` en desarrollo (recarga en caliente).
- **RNF4 — Configuración por entorno:** `API_GENERICA_URL`, `API_FACTURAS_URL`
  (defaults `http://localhost:8001/8002` para correr sin Docker), `SECRET_KEY`.
- **RNF5 — Timeouts:** 10 s para CRUD, 5 s para el chequeo de estado.
- **RNF6 — Degradación elegante:** API caída → flash de error + página vacía,
  nunca un traceback.
- **RNF7 — Todo en español** con comentarios didácticos (código Y plantillas).

## 5. Criterios de aceptación

1. `http://localhost:8000` carga con las dos APIs "en línea"; apagar una API
   (`docker compose stop api-generica`) y recargar → badge rojo "sin conexión".
2. Ciclo completo en Productos: crear PR009 → aparece en la lista → editar stock
   → eliminar con confirmación. Cada paso muestra su flash verde.
3. Cambiar la API activa a Facturas y repetir el punto 2: funciona igual;
   crear un producto sin nombre da error visible (validación Pydantic 422).
4. En Personas, intentar eliminar P001 (es cliente) → alerta roja con el error
   de llave foránea textual de la BD.
5. `/facturas/1` muestra el maestro y sus 1+ renglones; una factura anulada
   muestra badge rojo.
6. El Explorador muestra cualquiera de las 12 tablas con columnas correctas,
   incluida una tabla vacía ("Tabla vacía.").
7. Detener las APIs no tumba el front: cada pantalla muestra el error y sigue navegable.

## 6. Brechas conocidas (aceptadas en la versión original)

Documentadas para quien reconstruya: sin páginas 404/500 personalizadas; el
formulario de crear no repobla campos tras un error; `int()`/`float()` del POST
sin try/except (mitigado por `type="number"`); URLs de Swagger del inicio
hardcodeadas a localhost; sin paginación; `SECRET_KEY` con default de desarrollo.
