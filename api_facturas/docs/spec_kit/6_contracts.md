# Contratos HTTP — API Facturas

> **Documento 6 de 8** del spec kit: referencia exhaustiva de TODOS los endpoints
> ([2_spec.md](2_spec.md) · [3_plan.md](3_plan.md) · [5_data_model.md](5_data_model.md) · [8_tasks.md](8_tasks.md)).
> Base: `http://localhost:8002`. Documentación interactiva: `/docs` (Swagger UI) y `/redoc`.

---

## 0. Convenciones globales

**Sobre de respuesta en lecturas:**
```json
{ "tabla": "persona", "total": 6, "datos": [ { "codigo": "P001", "nombre": "Ana Torres", ... } ] }
```

**Respuestas de escritura:**
```json
// POST
{ "estado": 200, "mensaje": "Persona creada exitosamente.", "datos": { ...lo enviado... } }
// PUT
{ "estado": 200, "mensaje": "Persona actualizada exitosamente.", "filtro": "codigo = P001", "filasAfectadas": 1 }
// DELETE
{ "estado": 200, "mensaje": "Persona eliminada exitosamente.", "filtro": "codigo = P001", "filasEliminadas": 1 }
```

**Errores** — siempre `HTTPException` con `detail` estructurado (FastAPI lo anida):
```json
{ "detail": { "estado": 404, "mensaje": "No se encontró...", "detalle": "..." } }
```

| Código | Cuándo |
|---|---|
| 200 | Éxito (no se declaran `status_code` custom ni `response_model`) |
| 204 | Lista vacía (cuerpo vacío, `Response(status_code=204)`) |
| 400 | `ValueError` de validación del servicio (argumento vacío) |
| 404 | Registro no encontrado / 0 filas afectadas |
| 422 | Body no cumple el modelo Pydantic (lo genera FastAPI solo) |
| 500 | Error de BD (`RuntimeError` del repositorio: FK violada, PK duplicada, trigger) |

Query params comunes en todos los GET/POST/PUT/DELETE: `esquema` (opcional;
default `public`/`dbo`/ninguno según motor) y en listados `limite` (opcional,
tope interno 1000).

Las rutas de colección llevan **barra final** (`GET /api/persona/`); pedir
`/api/persona` produce redirect 307.

## 1. Patrón CRUD estándar

Aplica a: **persona** (pk `codigo`:str), **empresa** (`codigo`:str),
**producto** (`codigo`:str), **cliente** (`id`:int), **vendedor** (`id`:int),
**rol** (`id`:int), **factura** (`numero`:int), **usuario** (`email`:str),
**ruta** (`valor_ruta:path`:str).

```
GET    /api/<entidad>/            → 200 sobre | 204 vacío
GET    /api/<entidad>/{pk}        → 200 sobre | 404
POST   /api/<entidad>/            body = <Modelo>          → 200 | 422 | 500
PUT    /api/<entidad>/{pk}        body = <Modelo> (la API excluye la PK con
                                  model_dump(exclude={"<pk>"}))  → 200 | 404
DELETE /api/<entidad>/{pk}        → 200 | 404
```

Ejemplos concretos:

```
GET    /api/persona/                          # 6 personas
GET    /api/persona/P001                      # Ana Torres
POST   /api/producto/      {"codigo":"PR009","nombre":"Webcam","stock":5,"valorunitario":120000}
PUT    /api/producto/PR009 {"codigo":"PR009","nombre":"Webcam HD","stock":7,"valorunitario":120000}
DELETE /api/producto/PR009
GET    /api/factura/1                         # {"numero":1,"fecha":"2025-12-03T12:57:19...","total":5000000.0,...}
GET    /api/ruta//home                        # PK con barras gracias a {valor_ruta:path}
```

## 2. Endpoints especiales por entidad

### usuario — CRUD estándar MÁS:
```
POST /api/usuario/verificar-contrasena
     ?valor_usuario=admin@correo.com&valor_contrasena=admin123   [&esquema=]
→ 200 { "estado": 200, "mensaje": "Contraseña válida.",   "usuario": "admin@correo.com" }
→ 401 detail { "estado": 401, "mensaje": "Contraseña incorrecta.", ... }
→ 404 detail { "estado": 404, "mensaje": "Usuario no encontrado.", ... }
```
`POST /api/usuario/` y `PUT /api/usuario/{email}` encriptan `contrasena` con
BCrypt automáticamente (el repositorio declara `CAMPOS_ENCRIPTAR = "contrasena"`).
No existe `/login` ni emisión de tokens: solo verificación.

### productosporfactura — tabla puente, SIN PUT
```
GET    /api/productosporfactura/                       # todos los renglones
GET    /api/productosporfactura/factura/{fknumfactura} # renglones de UNA factura (int)
POST   /api/productosporfactura/                       # body = ProductosPorFactura
DELETE /api/productosporfactura/{fknumfactura}/{fkcodproducto}
```
El POST dispara el trigger de la BD (calcula subtotal, descuenta stock,
actualiza total); enviar `"subtotal": 0` es válido. Stock insuficiente → 500 con
el mensaje del trigger.

### rol_usuario — prefix con guion `/api/rol-usuario`, SIN PUT
```
GET    /api/rol-usuario/
GET    /api/rol-usuario/usuario/{fkemail}     # roles de un usuario
GET    /api/rol-usuario/rol/{fkidrol}         # usuarios de un rol
POST   /api/rol-usuario/                      # body = RolUsuario
DELETE /api/rol-usuario/{fkemail}/{fkidrol}
```

### rutarol — SIN PUT
```
GET    /api/rutarol/
GET    /api/rutarol/rol/{rol}                 # rutas asignadas a un rol
POST   /api/rutarol/                          # body = RutaRol
DELETE /api/rutarol/{valor_ruta}/{rol}
```

> ⚠️ **Comportamiento del código original en los 3 DELETE compuestos:** la ruta
> declara ambos segmentos pero el servicio solo filtra por el **primero**
> (borra todos los renglones de esa factura / todos los roles de ese usuario /
> todas las asignaciones de esa ruta). Al reconstruir, decidir: replicar fiel o
> corregir filtrando por ambas columnas. Ver [2_spec.md](2_spec.md) RF2.

## 3. Controller genérico de respaldo (prefix `/api`, registrado de ÚLTIMO)

Atrapa cualquier tabla SIN controller propio. Body de escritura: `dict` crudo
(sin validación Pydantic).

```
GET    /api/{tabla}                            ?esquema&limite      → 200|204
GET    /api/{tabla}/{nombre_clave}/{valor}     ?esquema             → 200|404
POST   /api/{tabla}                            ?esquema&campos_encriptar   body=dict → 200|400
PUT    /api/{tabla}/{nombre_clave}/{valor}     ?esquema&campos_encriptar   body=dict → 200|404
DELETE /api/{tabla}/{nombre_clave}/{valor}     ?esquema             → 200|404
POST   /api/{tabla}/verificar-contrasena       ?campo_usuario&campo_contrasena&valor_usuario&valor_contrasena[&esquema]
```

`campos_encriptar`: nombres de columnas separados por coma cuyos valores se
guardan como hash BCrypt. Mapeo de excepciones: `ValueError`→400,
`PermissionError`→403, `LookupError`→404, resto→500.

## 4. Diagnóstico

```
GET /  →  { "mensaje": "API Facturas CRUD activa.", "docs": "/docs", "redoc": "/redoc" }
```

Cualquier consumidor puede usar este endpoint como healthcheck (p. ej. para un
badge de "API en línea").

## 5. Tabla resumen de los 13 routers

| Router | Prefix | Tags | Endpoints |
|---|---|---|---|
| persona | `/api/persona` | Persona | CRUD 5 |
| empresa | `/api/empresa` | Empresa | CRUD 5 |
| cliente | `/api/cliente` | Cliente | CRUD 5 |
| vendedor | `/api/vendedor` | Vendedor | CRUD 5 |
| producto | `/api/producto` | Producto | CRUD 5 |
| factura | `/api/factura` | Factura | CRUD 5 |
| detalle | `/api/productosporfactura` | ProductosPorFactura | 4 (sin PUT, + /factura/{n}) |
| usuario | `/api/usuario` | Usuario | CRUD 5 + verificar-contrasena |
| rol | `/api/rol` | Rol | CRUD 5 |
| rol_usuario | `/api/rol-usuario` | RolUsuario | 5 (sin PUT, + 2 búsquedas) |
| ruta | `/api/ruta` | Ruta | CRUD 5 (con `:path`) |
| rutarol | `/api/rutarol` | RutaRol | 5 (sin PUT, + 1 búsqueda) |
| entidades | `/api` | Entidades | 6 genéricos (de último) |
