# Contratos — Frontend Flask

> **Documento 6 de 8** del spec kit. Dos contratos: (1) las rutas que el front
> EXPONE al navegador y (2) los endpoints que CONSUME de las dos APIs (lo que
> necesita saber de ellas para construirse sin leer sus proyectos).

---

## 1. Rutas propias (lo que ve el navegador)

| Método | Ruta | Endpoint (blueprint.función) | Hace |
|---|---|---|---|
| GET | `/` | `inicio.pagina_inicio` | Estado de las 2 APIs + tarjetas |
| GET | `/cambiar-api/<nombre>` | `cambiar_api` (en app.py, sin blueprint) | Guarda la API activa en sesión y vuelve al referrer |
| GET | `/productos/` | `productos.listar` | Tabla de productos |
| GET·POST | `/productos/nuevo` | `productos.crear` | Formulario / crea y redirige |
| GET·POST | `/productos/editar/<codigo>` | `productos.editar` | Formulario repoblado / actualiza |
| POST | `/productos/eliminar/<codigo>` | `productos.eliminar` | Elimina y redirige |
| GET | `/personas/` | `personas.listar` | Tabla de personas |
| GET·POST | `/personas/nuevo` | `personas.crear` | Formulario / crea |
| GET·POST | `/personas/editar/<codigo>` | `personas.editar` | Formulario / actualiza |
| POST | `/personas/eliminar/<codigo>` | `personas.eliminar` | Elimina |
| GET | `/facturas/` | `facturas.listar` | Lista de facturas |
| GET | `/facturas/<int:numero>` | `facturas.detalle` | Maestro-detalle |
| GET | `/explorador/?tabla=<nombre>` | `explorador.explorar` | Tabla dinámica (default `persona`) |

En plantillas: `url_for('productos.listar')`, `url_for('cambiar_api', nombre='facturas')`, etc.

## 2. Lo que el front necesita de las APIs

Ambas APIs cumplen el mismo contrato lógico con dos variantes de URL. `ClienteApi`
elige la base según la API activa:

| | API Genérica | API Facturas |
|---|---|---|
| URL base (env) | `API_GENERICA_URL` (default `http://localhost:8001`) | `API_FACTURAS_URL` (default `http://localhost:8002`) |
| Listar tabla | `GET {base}/api/{tabla}` | `GET {base}/api/{tabla}/` ← **barra final** |
| Un registro | `GET {base}/api/{tabla}/{clave}/{valor}` | `GET {base}/api/{tabla}/{valor}` ← la API ya conoce su PK |
| Crear | `POST` a la URL de listar, body JSON | igual |
| Actualizar | `PUT` a la URL de registro, body JSON | igual |
| Eliminar | `DELETE` a la URL de registro | igual |
| Healthcheck | `GET {base}/` → JSON con `mensaje` | igual |

**Sobre de respuesta esperado en lecturas** (ambas APIs):
```json
{ "tabla": "producto", "total": 8, "datos": [ { ... }, ... ] }
```
- `204` en listar = tabla vacía → el cliente lo traduce a lista vacía.
- El front usa `datos` y, en `obtener`, toma `datos[0]`.

**Formato de error esperado** (FastAPI): `{"detail": {...}}` donde `detail`
puede ser dict con claves `detalle` y/o `mensaje`, o un string. El cliente
extrae en ese orden; si el cuerpo no es JSON → `"Error HTTP {status}"`; si no
hubo respuesta → `"No se pudo conectar con la API: {excepción}"`.

**Tablas/claves usadas por el front:**

| Pantalla | tabla | clave (para la API genérica) |
|---|---|---|
| Productos | `producto` | `codigo` |
| Personas | `persona` | `codigo` |
| Facturas | `factura` | `numero` |
| Detalle factura | `productosporfactura` | — (se lista completa) |
| Explorador | las 12 | — (solo listar) |

## 3. Contrato interno `ClienteApi` (para las rutas)

```python
ClienteApi(nombre_api: str)          # "generica" | "facturas" (otro valor → generica)

listar(tabla)                 -> (True, list[dict]) | (False, str_mensaje)
obtener(tabla, clave, valor)  -> (True, dict)       | (False, "No existe {tabla} con {clave} = {valor}") | (False, msg)
crear(tabla, datos)           -> (True, "Registro creado correctamente.")      | (False, msg)
actualizar(tabla, clave, valor, datos) -> (True, "Registro actualizado correctamente.") | (False, msg)
eliminar(tabla, clave, valor) -> (True, "Registro eliminado correctamente.")   | (False, msg)
estado()                      -> dict (JSON de GET /) | None
```

Timeouts: 10 s en CRUD, 5 s en `estado()`. El cliente **nunca lanza** excepciones
hacia las rutas. Los mensajes de éxito son literales (terminan en punto) y se
muestran tal cual como flash.

## 4. Variables de entorno

| Variable | Default (sin Docker) | Ejemplo en docker-compose (hosts internos) |
|---|---|---|
| `API_GENERICA_URL` | `http://localhost:8001` | `http://api-generica:8001` |
| `API_FACTURAS_URL` | `http://localhost:8002` | `http://api-facturas:8002` |
| `SECRET_KEY` | `clave-de-desarrollo-paradigmas` | (no se define → default) |
