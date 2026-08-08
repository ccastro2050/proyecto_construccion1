# Contratos HTTP — API Genérica C# (ASP.NET Core)

> **Documento 6 de 8** del spec kit: los endpoints con formatos exactos.
> Base: `http://localhost:8013`. Documentación interactiva: `/swagger` (con botón
> **Authorize**) y `/redoc` (OpenAPI en `/swagger/v1/swagger.json`).

---

## 0. Convenciones globales

- Éxitos con envoltura de metadatos; errores SIEMPRE como objeto plano:

```json
{ "estado": 400, "mensaje": "Parámetros inválidos.", "detalle": "...", "tabla": "..." }
```

| Excepción interna | HTTP |
|---|---|
| `ArgumentException` (validación) | 400 |
| Token ausente/inválido en endpoint `[Authorize]` | 401 (lo emite el middleware JWT, sin cuerpo) |
| `UnauthorizedAccessException` (tabla prohibida) | 403 |
| `InvalidOperationException` / sin filas | 404 (lecturas) · 500 (escrituras) |
| cualquier otra | 500 (con `tipoError` y detalle del motor) |

- Query param `esquema` opcional en los endpoints de entidades; default por
  motor: `public` (PostgreSQL) / la BD de la conexión (MariaDB) / `dbo` (SQL Server).

## 1. `POST /api/Autenticacion/token` — Emitir JWT

Body (genérico — sirve para cualquier tabla de usuarios):

```
POST /api/Autenticacion/token
body { "tabla": "usuario", "campoUsuario": "email", "campoContrasena": "contrasena",
       "usuario": "admin@correo.com", "contrasena": "admin123" }
→ 200 { "estado": 200, "mensaje": "Autenticación exitosa.", "usuario": "admin@correo.com",
        "token": "eyJhbGciOiJIUzI1NiIs...", "expiracion": "2026-07-31T14:00:00Z" }
→ 400 body incompleto (incluye un "ejemplo" en la respuesta)
→ 404 { "estado": 404, "mensaje": "Usuario no encontrado." }
→ 401 { "estado": 401, "mensaje": "Contraseña incorrecta." }
```

Token HS256 con claims `Name`, `tabla`, `campoUsuario`; expira en
`Jwt:DuracionMinutos` (60). Se usa como `Authorization: Bearer {token}`.

## 2. `GET /api/{tabla}` — Listar 🔒 **requiere JWT**

Query: `esquema`, `limite` (default interno 1000).

```
GET /api/producto?limite=50          (con Authorization: Bearer …)
→ 200 { "tabla": "producto", "esquema": "por defecto", "limite": 50,
        "total": 8, "datos": [ { "codigo": "PR001", "nombre": "Laptop Lenovo IdeaPad",
                                 "stock": 17, "valorunitario": 2500000 }, ... ] }
→ 204 (cuerpo vacío) si la tabla no tiene filas
→ 401 sin token o token vencido
→ 404 si la tabla no existe (con "sugerencia" en el cuerpo)
```

Es el **único** endpoint con `[Authorize]` — los demás son anónimos a propósito
(ver [4_research.md](4_research.md) D5).

## 3. `GET /api/{tabla}/{nombreClave}/{valor}` — Filtrar por clave

El valor llega como texto y el repositorio lo castea al tipo real de la columna.
Devuelve LISTA (una clave no única puede traer varias filas).

```
GET /api/factura/numero/1
→ 200 { "tabla": "factura", "esquema": "por defecto", "filtro": "numero = 1",
        "total": 1, "datos": [ { "numero": 1, "fecha": "...", "total": 5000000, ... } ] }
→ 404 { "estado": 404, "mensaje": "No se encontraron registros",
        "detalle": "No se encontró ningún registro con numero = 99 en la tabla factura", ... }

GET /api/factura/fecha/2025-12-03     ← fecha sin hora sobre columna TIMESTAMP
→ 200 con las facturas de ese día (compara CAST(fecha AS DATE))
```

## 4. `POST /api/{tabla}` — Crear

Body: JSON plano `{columna: valor, ...}` (sin validación de esquema — la BD decide).
Query extra: `camposEncriptar` (CSV de columnas a guardar como hash BCrypt).

```
POST /api/persona     body {"codigo":"P999","nombre":"Test","email":"t@t.co","telefono":"300"}
→ 200 { "estado": 200, "mensaje": "Registro creado exitosamente.",
        "tabla": "persona", "esquema": "por defecto" }
→ 400 si el body viene vacío
→ 500 si la BD rechaza (PK duplicada, FK, columna inexistente) — error del motor en detalle

POST /api/usuario?camposEncriptar=contrasena
     body {"email":"qa@test.com","contrasena":"secreto1"}
→ 200; en la BD queda un hash $2a$10$... de 60 caracteres
```

## 5. `PUT /api/{tabla}/{nombreClave}/{valorClave}` — Actualizar

Body: JSON con las columnas a cambiar (solo esas). Soporta `camposEncriptar`.

```
PUT /api/persona/codigo/P999      body {"nombre":"Test Editado"}
→ 200 { "estado": 200, "mensaje": "Registro actualizado exitosamente.",
        "tabla": "persona", "esquema": "por defecto", "filtro": "codigo = P999",
        "filasAfectadas": 1, "camposEncriptados": "ninguno" }
→ 404 si ninguna fila coincide con la clave
```

## 6. `DELETE /api/{tabla}/{nombreClave}/{valorClave}` — Eliminar

```
DELETE /api/persona/codigo/P999
→ 200 { "estado": 200, "mensaje": "Registro eliminado exitosamente.",
        "tabla": "persona", "esquema": "por defecto", "filtro": "codigo = P999",
        "filasEliminadas": 1 }
→ 404 si ninguna fila coincide
→ 500 si la BD lo impide (FK) — p. ej. eliminar una persona que es cliente
```

## 7. `POST /api/{tabla}/verificar-contrasena` — Verificar credenciales

Query params: `campoUsuario`, `campoContrasena`, `valorUsuario`, `valorContrasena`
(+ `esquema` opcional). Compara con BCrypt contra el hash almacenado.

```
→ 200 contraseña válida · 401 incorrecta · 404 usuario no existe
```

Es la misma verificación que usa internamente `/api/Autenticacion/token`, pero
sin emitir token.

## 8. `POST /api/consultas/ejecutarconsultaparametrizada` — SELECT parametrizado

```
POST /api/consultas/ejecutarconsultaparametrizada
body { "consulta": "SELECT * FROM producto WHERE stock > @minimo",
       "parametros": { "minimo": 20 } }
→ 200 { "resultados": [ {columnas en minúsculas...} ], "total": 5, "advertencia": null }
→ 404 (texto) si la consulta corre pero no devuelve filas
→ 403 { "estado": 403, "mensaje": "Acceso denegado por políticas de seguridad.", ... }
      si toca una tabla de TablasProhibidas o no es SELECT
→ 400 consulta vacía o parámetros malformados
```

Tope de 10 000 filas; al alcanzarlo, `advertencia` lo indica.

## 9. `POST /api/procedimientos/ejecutarsp` — Procedimientos almacenados

```
POST /api/procedimientos/ejecutarsp
body { "nombreSP": "select_json_entity", "p_table_name": "usuario",
       "mensaje": "", "where_condition": null, "order_by": null,
       "limit_clause": null, "json_params": "{}", "select_columns": "*" }
→ 200 { "procedimiento": "select_json_entity", "resultados": [...],
        "total": 8, "mensaje": "Procedimiento ejecutado correctamente" }
→ 400 falta "nombreSP" · 500 con detalle del motor si el SP falla
```

Todo lo que no sea `nombreSP` se pasa como parámetro del SP (CALL/EXEC según motor).

## 10. `GET /api/estructuras/…` — Metadatos

```
GET /api/estructuras/producto/modelo[?esquema=]
→ 200 { "datos": [ {columna, tipo, nullable, default, ...} ], "total": 4 }
→ 404 (texto) si la tabla no existe en ningún esquema

GET /api/estructuras/basedatos
→ 200 { tablas, vistas, funciones, procedimientos, triggers, ... }  (según motor)
```

## 11. `GET /api/diagnostico/conexion` — Diagnóstico

```
→ 200 { "estado": 200, "mensaje": "Diagnóstico de conexión obtenido exitosamente.",
        "servidor": { proveedor, baseDatos, version, servidor, horaInicio, usuarioConectado, ... },
        "configuracion": { "proveedorConfigurado": "postgres", ... }, "timestamp": "..." }
→ 501 si el motor activo no implementa diagnóstico
```

Sin credenciales ni cadena de conexión — solo metadatos. La `horaInicio` del
servidor sirve para distinguir el contenedor Docker de un motor local.

## 12. `GET /` y `GET /api/info` — Bienvenida y ayuda

```
GET /          → 200 { mensaje: "Bienvenido a la API Genérica en C#", version, enlaces: {swagger, info, ...}, uso: [...] }
GET /api/info  → 200 { controlador, version, descripcion, endpoints: [...], ejemplos: [...] }
```

(Los nombres salen en camelCase/minúsculas: es la serialización por defecto de ASP.NET Core.)

Usables como healthcheck / verificación de "en línea".
