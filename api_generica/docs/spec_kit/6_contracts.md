# Contratos HTTP — API Genérica CRUD

> **Documento 6 de 8** del spec kit: los 7 endpoints con formatos exactos.
> Base: `http://localhost:8001`. Documentación interactiva: `/swagger` y `/redoc`
> (OpenAPI en `/swagger/v1/swagger.json`).

---

## 0. Convenciones globales

- Router con prefix `/api`, tag `Entidades`.
- Query param `esquema` (opcional) en todos; default por motor:
  `public` (PostgreSQL) / la BD de la conexión (MariaDB) / `dbo` (SQL Server).
- Errores SIEMPRE como `HTTPException` con `detail` estructurado:

```json
{ "detail": { "estado": 400, "mensaje": "Parámetros inválidos.", "detalle": "..." } }
```

| Excepción interna | HTTP |
|---|---|
| `ValueError` (validación del servicio) | 400 |
| `PermissionError` | 403 |
| `LookupError` / sin filas | 404 |
| cualquier otra (`RuntimeError` del repo con el error del motor) | 500 |

## 1. `GET /api/{tabla}` — Listar

Query: `esquema`, `limite` (default interno 1000).

```
GET /api/producto?limite=50
→ 200 { "tabla": "producto", "esquema": "por defecto", "limite": 50,
        "total": 8, "datos": [ { "codigo": "PR001", "nombre": "Laptop Lenovo IdeaPad",
                                 "stock": 17, "valorunitario": 2500000.0 }, ... ] }
→ 204 (cuerpo vacío) si la tabla no tiene filas
→ 500 si la tabla no existe (error del motor en detalle)
```

## 2. `GET /api/{tabla}/{nombre_clave}/{valor}` — Filtrar por clave

El valor llega como texto y la API lo convierte al tipo real de la columna
([5_data_model.md](5_data_model.md) §1). Devuelve LISTA (una clave no única
puede traer varias filas).

```
GET /api/factura/numero/1
→ 200 { "tabla": "factura", "esquema": "por defecto", "filtro": "numero = 1",
        "total": 1, "datos": [ { "numero": 1, "fecha": "2025-12-03T12:57:19.275920",
                                 "total": 5000000.0, "estado": "activa",
                                 "fkidcliente": 1, "fkidvendedor": 1 } ] }
→ 404 { detail: { estado: 404, mensaje: "No se encontró ningún registro con numero = 99 en factura" } }

GET /api/factura/fecha/2025-12-03      ← fecha sin hora sobre columna TIMESTAMP
→ 200 con las facturas de ese día (compara CAST(fecha AS DATE))
```

## 3. `POST /api/{tabla}` — Crear

Body: JSON plano `{columna: valor, ...}` (sin validación de esquema — la BD decide).
Query extra: `campos_encriptar` (CSV de columnas a guardar como hash BCrypt).

```
POST /api/persona        body {"codigo":"P999","nombre":"Test","email":"t@t.co","telefono":"300"}
→ 200 { "estado": 200, "mensaje": "Registro creado exitosamente.",
        "tabla": "persona", "esquema": "por defecto" }
→ 400 si el body viene vacío
→ 500 si la BD rechaza (PK duplicada, FK, columna inexistente) — error del motor en detalle

POST /api/usuario?campos_encriptar=contrasena
     body {"email":"qa@test.com","contrasena":"secreto1"}
→ 200; en la BD queda un hash $2b$12$... de 60 caracteres
```

## 4. `PUT /api/{tabla}/{nombre_clave}/{valor_clave}` — Actualizar

Body: JSON con las columnas a cambiar (solo esas). Soporta `campos_encriptar`.

```
PUT /api/persona/codigo/P999      body {"nombre":"Test Editado"}
→ 200 { "estado": 200, "mensaje": "Registro actualizado exitosamente.",
        "tabla": "persona", "filtro": "codigo = P999", "filasAfectadas": 1 }
→ 404 si ninguna fila coincide con la clave
```

## 5. `DELETE /api/{tabla}/{nombre_clave}/{valor_clave}` — Eliminar

```
DELETE /api/persona/codigo/P999
→ 200 { "estado": 200, "mensaje": "Registro eliminado exitosamente.",
        "tabla": "persona", "filtro": "codigo = P999", "filasEliminadas": 1 }
→ 404 si ninguna fila coincide
→ 500 si la BD lo impide (FK) — p. ej. eliminar una persona que es cliente
```

## 6. `POST /api/{tabla}/verificar-contrasena` — Verificar credenciales

Todos por query (obligatorios salvo `esquema`): `campo_usuario`,
`campo_contrasena`, `valor_usuario`, `valor_contrasena`.

```
POST /api/usuario/verificar-contrasena?campo_usuario=email&campo_contrasena=contrasena&valor_usuario=qa@test.com&valor_contrasena=secreto1
→ 200 { "estado": 200, "mensaje": "Contraseña válida.", "usuario": "qa@test.com" }
→ 401 detail { estado: 401, mensaje: "Contraseña incorrecta.", usuario: ... }
→ 404 detail { estado: 404, mensaje: "Usuario no encontrado.", usuario: ... }
```

Compara con BCrypt (`checkpw`) contra el hash almacenado. Genérico: sirve para
cualquier tabla que tenga un campo usuario + un campo hash.

## 7. `GET /` — Diagnóstico (fuera de `/api`, tag `Diagnóstico`)

```
GET /
→ 200 { "mensaje": "API CRUD genérica funcionando", "version": "1.0.0",
        "entorno": "production", "documentacion": { "swagger": "/swagger", "redoc": "/redoc" } }
```

Usable como healthcheck por cualquier cliente (p. ej. para un badge de
"API en línea").
