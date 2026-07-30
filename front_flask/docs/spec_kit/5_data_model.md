# Modelo de datos — Frontend Flask

> **Documento 5 de 8** del spec kit · **Informativo**: el front NO tiene base de
> datos propia ni modelos — consume JSON de las APIs. Este documento describe
> los datos que cada pantalla espera recibir y qué hace con ellos.

---

## 1. El "modelo" del front: diccionarios JSON tal cual llegan

Las APIs devuelven filas como objetos JSON planos dentro del sobre
`{"tabla", "total", "datos": [...]}`. El front NO define clases: pasa los dicts
directo a Jinja y accede por clave (`p.codigo`, `f["fecha"]`). Las claves son
los nombres de columna de la BD, en minúsculas y sin separadores.

## 2. Datos por pantalla

### Productos (`producto`)
| Campo | Tipo JSON | Uso en la vista |
|---|---|---|
| `codigo` | str | PK; `<code>`, path de editar/eliminar; input ≤10 chars |
| `nombre` | str | texto; input ≤100 chars |
| `stock` | int | columna alineada a la derecha; input number min 0 |
| `valorunitario` | float | formato `$ {{ "{:,.0f}".format(v \| float) }}`; input number step 0.01 |

Formulario POST envía: `codigo` (solo crear), `nombre`, `stock`→int,
`valorunitario`→float.

### Personas (`persona`)
| Campo | Tipo | Uso |
|---|---|---|
| `codigo` | str | PK; input ≤10 |
| `nombre` | str | input ≤100 |
| `email` | str | input `type=email` ≤100 |
| `telefono` | str | input ≤20 |

### Facturas (`factura`) — solo lectura
| Campo | Tipo | Uso |
|---|---|---|
| `numero` | int | PK; path del detalle (`<int:numero>`) |
| `fecha` | str ISO (`2025-12-03T12:57:19.275920`) | lista: `fecha[:10]`; detalle: `fecha[:19]` con `T`→espacio |
| `estado` | str | badge: rojo si `"anulada"`, verde en otro caso; default visual `"activa"` |
| `total` | float | formato moneda; **viene calculado por la BD, no se recalcula** |
| `fkidcliente` / `fkidvendedor` | int | se muestran como ids (sin resolver nombre) |

### Detalle de factura (`productosporfactura`) — solo lectura
| Campo | Tipo | Uso |
|---|---|---|
| `fknumfactura` | int | filtro en Python: `== numero` del path |
| `fkcodproducto` | str | `<code>` |
| `cantidad` | int | derecha |
| `subtotal` | float | derecha; calculado por la BD |

### Explorador — cualquier tabla
Sin esquema fijo: `columnas = list(filas[0].keys())` y celdas `fila[c]`.
Lista de tablas hardcodeada (12, en este orden): empresa, persona, producto,
cliente, vendedor, factura, productosporfactura, usuario, rol, rol_usuario,
ruta, rutarol.

### Inicio — estado de las APIs
`estado()` devuelve el JSON de `GET {base}/` o `None`; las plantillas solo
evalúan verdad/falsedad (badge verde/rojo), no leen campos.

## 3. Estado propio del front (lo único que "persiste")

| Dónde | Clave | Valores | Uso |
|---|---|---|---|
| `flask.session` (cookie firmada con `SECRET_KEY`) | `"api"` | `"generica"` \| `"facturas"` (default `"generica"`) | API activa; la inyecta el context processor como `api_activa` |
| Mensajes flash (van en la misma cookie de sesión) | categoría | `"success"` \| `"danger"` | alertas Bootstrap tras cada acción |

No hay ninguna otra persistencia: sin BD, sin archivos, sin caché.
