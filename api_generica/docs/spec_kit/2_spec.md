# Especificación — API Genérica CRUD

> **Documento 2 de 8** de un spec kit **autocontenido**: con esta carpeta se
> reconstruye la API completa desde cero, como proyecto independiente.
>
> | # | Documento | Contenido |
> |---|---|---|
> | 1 | [1_constitution.md](1_constitution.md) | Principios innegociables |
> | 2 | **2_spec.md** (este) | QUÉ construir: requisitos y criterios de aceptación |
> | 3 | [3_plan.md](3_plan.md) | CÓMO: stack, estructura, diseño de cada capa |
> | 4 | [4_research.md](4_research.md) | Decisiones técnicas y alternativas *(lectura opcional)* |
> | 5 | [5_data_model.md](5_data_model.md) | Qué descubre en runtime + la BD de prueba bdfacturas |
> | 6 | [6_contracts.md](6_contracts.md) | Los 7 endpoints con formatos exactos |
> | 7 | [7_quickstart.md](7_quickstart.md) | Arranque y smoke test de validación |
> | 8 | [8_tasks.md](8_tasks.md) | Orden de construcción por fases verificables |

---

## 1. Propósito

Construir una **API REST genérica** capaz de hacer operaciones CRUD (crear, leer,
actualizar, eliminar) sobre **cualquier tabla** de una base de datos, sin conocer
de antemano sus columnas, y funcionando por igual contra **PostgreSQL,
MySQL/MariaDB y SQL Server** con solo cambiar una variable de entorno.

La idea central: en lugar de escribir un endpoint por tabla, se escribe **un solo
conjunto de endpoints parametrizados por el nombre de la tabla** (`/api/{tabla}`).
La API descubre los tipos de las columnas consultando el catálogo del motor
(`information_schema`) y convierte los valores automáticamente.

## 2. Alcance

**Incluye:**
- CRUD genérico sobre cualquier tabla del esquema por defecto (u otro esquema vía query param).
- Selección del motor de base de datos por configuración (`DB_PROVIDER`), sin tocar código.
- Encriptación BCrypt de campos indicados por el cliente (p. ej. contraseñas).
- Verificación de credenciales (comparar texto plano contra hash BCrypt almacenado).
- Documentación interactiva Swagger.

**No incluye:**
- Validación de campos por entidad (eso lo hace la API de Facturas con Pydantic).
- Autenticación/autorización de la API misma (es un proyecto didáctico).
- Migraciones de esquema (las BD se crean con scripts `init.sql` externos).

## 3. Requisitos funcionales

### RF1 — Listar registros
`GET /api/{tabla}` devuelve las filas de la tabla.
- Query params opcionales: `esquema` (esquema de BD) y `limite` (máx. de filas; por defecto 1000).
- Respuesta 200 con envoltura: `{ "tabla", "esquema", "limite", "total", "datos": [...] }`.
- Si la tabla está vacía → **204 Sin contenido** (cuerpo vacío).

### RF2 — Filtrar por clave
`GET /api/{tabla}/{nombre_clave}/{valor}` devuelve las filas donde la columna
`nombre_clave` es igual a `valor`.
- El valor llega como texto en la URL; la API debe **convertirlo al tipo real de la
  columna** (entero, decimal, fecha, uuid, booleano…) antes de comparar.
- Caso especial: si la columna es `TIMESTAMP` y el valor tiene formato `YYYY-MM-DD`,
  se compara solo la parte de fecha (`CAST(col AS DATE) = valor`).
- Sin resultados → 404 con mensaje descriptivo.

### RF3 — Crear registro
`POST /api/{tabla}` con body JSON `{columna: valor, ...}` inserta una fila.
- Query param opcional `campos_encriptar`: lista de columnas separadas por coma
  cuyos valores deben guardarse como hash BCrypt (p. ej. `contrasena`).
- Éxito → 200 con `{ "estado": 200, "mensaje": "Registro creado exitosamente.", ... }`.
- Body vacío → 400.

### RF4 — Actualizar registro
`PUT /api/{tabla}/{nombre_clave}/{valor_clave}` con body JSON actualiza las filas
que coinciden con la clave.
- Soporta `campos_encriptar` igual que RF3.
- Devuelve `filasAfectadas`; si es 0 → 404.

### RF5 — Eliminar registro
`DELETE /api/{tabla}/{nombre_clave}/{valor_clave}` elimina las filas que coinciden.
- Devuelve `filasEliminadas`; si es 0 → 404.

### RF6 — Verificar contraseña
`POST /api/{tabla}/verificar-contrasena` con query params `campo_usuario`,
`campo_contrasena`, `valor_usuario`, `valor_contrasena`.
- Busca el hash almacenado y lo compara con BCrypt.
- 200 contraseña válida · 404 usuario no existe · 401 contraseña incorrecta.

### RF7 — Endpoint de diagnóstico
`GET /` devuelve un JSON con mensaje, versión, entorno y rutas de documentación.
Sirve para que el frontend verifique que la API está "en línea".

### RF8 — Selección de motor por configuración
La variable `DB_PROVIDER` decide el motor: `postgres` (alias `postgresql`),
`mariadb` (alias `mysql`), `sqlserver` (alias `sqlserverexpress`, `localdb`).
Las cadenas de conexión llegan por variables `DB_POSTGRES`, `DB_MARIADB`,
`DB_MYSQL`, `DB_SQLSERVER`. Cambiar de motor **no requiere cambiar código**.

## 4. Requisitos no funcionales

- **RNF1 — Asíncrona:** todas las operaciones de BD usan drivers async
  (la API no se bloquea mientras espera a la base de datos).
- **RNF2 — Manejo de errores uniforme:** todas las respuestas de error tienen el
  formato `{ "estado": <código>, "mensaje": "...", "detalle": "..." }` con códigos
  400 (parámetros inválidos), 403, 404, 500.
- **RNF3 — CORS abierto:** cualquier origen puede consumir la API (es la única
  forma de que un frontend en otro puerto la llame desde el navegador).
- **RNF4 — Swagger en `/swagger`** (no en el `/docs` por defecto de FastAPI),
  con OpenAPI en `/swagger/v1/swagger.json`.
- **RNF5 — Serialización JSON segura:** `datetime`/`date` → ISO 8601,
  `Decimal` → float, `UUID` → string.
- **RNF6 — Contenedor Docker:** la API corre en el puerto **8001** dentro de la
  arquitectura de 3 capas del proyecto (ver spec kit raíz en `docs/spec_kit/`).

## 5. Criterios de aceptación

1. `docker compose up -d` y `GET http://localhost:8001/` responde con el JSON de diagnóstico.
2. `GET /api/producto` devuelve los 8 productos de ejemplo con envoltura `{total, datos}`.
3. `GET /api/factura/numero/1` devuelve la factura 1 (conversión texto→entero automática).
4. `POST /api/persona` con `{"codigo":"P999","nombre":"Test","email":"t@t.co","telefono":"300"}`
   crea la fila; se ve en el Explorador del front y con un cliente SQL.
5. `PUT /api/persona/codigo/P999` cambia el nombre; `DELETE /api/persona/codigo/P999` la elimina.
6. `POST /api/usuario?campos_encriptar=contrasena` guarda la contraseña como hash
   BCrypt de 60 caracteres (verificable en la tabla), y
   `POST /api/usuario/verificar-contrasena` responde 200 con la contraseña original.
7. Repetir los puntos 2–5 con `DB_PROVIDER=mariadb` y `DB_PROVIDER=sqlserver`:
   el comportamiento es idéntico.
8. Tabla vacía → 204; tabla inexistente → 500 con detalle del motor; clave sin
   coincidencias en PUT/DELETE → 404.

## 6. Glosario

| Término | Significado |
|---|---|
| Repositorio | Clase que sabe hablar SQL con UN motor concreto |
| Servicio | Clase con la lógica de negocio, ignorante del motor |
| Proveedor (provider) | Nombre del motor activo (`postgres`, `mariadb`, `sqlserver`) |
| Fábrica (factory) | Función que elige qué repositorio instanciar según el proveedor |
| Contrato / interfaz | `Protocol` de Python que define QUÉ métodos debe tener una clase |
