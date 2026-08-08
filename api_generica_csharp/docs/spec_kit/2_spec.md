# Especificación — API Genérica C# (ASP.NET Core)

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
> | 6 | [6_contracts.md](6_contracts.md) | Los endpoints con formatos exactos |
> | 7 | [7_quickstart.md](7_quickstart.md) | Arranque y smoke test de validación |
> | 8 | [8_tasks.md](8_tasks.md) | Orden de construcción por fases verificables |

---

## 1. Propósito

Construir en **C# / ASP.NET Core** una **API REST genérica** capaz de hacer
operaciones CRUD sobre **cualquier tabla** de una base de datos, sin conocer de
antemano sus columnas (`/api/{tabla}`), funcionando por igual contra
**PostgreSQL, MySQL/MariaDB y SQL Server** con solo cambiar una configuración —
más las capacidades que completan una API de plataforma: **autenticación JWT**,
**consultas SELECT parametrizadas**, **ejecución de procedimientos
almacenados** y **exploración de la estructura de la BD**.

La idea central: en lugar de escribir un endpoint por tabla, se escribe **un
solo conjunto de endpoints parametrizados por el nombre de la tabla**, y cada
fila viaja como un diccionario columna→valor descubierto en runtime.

## 2. Alcance

**Incluye:**
- CRUD genérico sobre cualquier tabla del esquema por defecto (u otro esquema
  vía query param).
- Selección del motor por configuración (`DatabaseProvider`), sin tocar código.
- Encriptación BCrypt de campos indicados por el cliente (`camposEncriptar`).
- Verificación de credenciales contra hash BCrypt.
- Emisión de **tokens JWT** contra cualquier tabla de usuarios; `GET /api/{tabla}`
  protegido con `[Authorize]`.
- Ejecución segura de consultas **SELECT** parametrizadas (con política de
  tablas prohibidas) y de **procedimientos almacenados**.
- Endpoints de metadatos: estructura de una tabla y de toda la BD; diagnóstico
  de conexión.
- Documentación Swagger + ReDoc.

**No incluye:**
- Validación de campos por entidad (decisión de diseño: la genericidad excluye
  modelos por tabla; la BD valida columnas y tipos).
- Autorización por roles (el JWT autentica, no discrimina permisos).
- Migraciones de esquema (las BD se crean con los scripts de `script_bd/`).

## 3. Requisitos funcionales

### RF1 — Listar registros (protegido con JWT)
`GET /api/{tabla}` devuelve las filas de la tabla. **Requiere token Bearer.**
- Query params opcionales: `esquema` y `limite` (por defecto 1000).
- 200 con envoltura `{tabla, esquema, limite, total, datos}`; tabla vacía → **204**.

### RF2 — Filtrar por clave
`GET /api/{tabla}/{nombreClave}/{valor}` devuelve las filas donde la columna
coincide. El valor llega como texto y se convierte al tipo real de la columna;
si la columna es fecha/hora y el valor es `YYYY-MM-DD`, compara solo la fecha
(`CAST(col AS DATE)`). Sin resultados → 404.

### RF3 — Crear registro
`POST /api/{tabla}` con body JSON `{columna: valor, ...}`.
- Query param opcional `camposEncriptar` (CSV de columnas a guardar como hash BCrypt).
- Éxito → 200 `{estado, mensaje, tabla, esquema}`; body vacío → 400.

### RF4 — Actualizar registro
`PUT /api/{tabla}/{nombreClave}/{valorClave}` con body JSON. Soporta
`camposEncriptar`. Devuelve `filasAfectadas`; si es 0 → 404.

### RF5 — Eliminar registro
`DELETE /api/{tabla}/{nombreClave}/{valorClave}`. Devuelve `filasEliminadas`;
si es 0 → 404.

### RF6 — Verificar contraseña
`POST /api/{tabla}/verificar-contrasena`: compara texto plano contra el hash
BCrypt almacenado. 200 válida · 404 usuario no existe · 401 incorrecta.

### RF7 — Emitir token JWT
`POST /api/Autenticacion/token` con body
`{tabla, campoUsuario, campoContrasena, usuario, contrasena}`:
verifica credenciales (RF6 por dentro) y, si son válidas, responde
`{estado, mensaje, usuario, token, expiracion}` con un JWT HS256 de 60 minutos.
El token abre el acceso a RF1.

### RF8 — Consultas SELECT parametrizadas
`POST /api/consultas/ejecutarconsultaparametrizada` con body
`{consulta, parametros}`. Solo **SELECT**; los parámetros viajan con `@nombre`;
las tablas de `TablasProhibidas` producen 403. Respuesta
`{Resultados, Total, Advertencia}` (advertencia al llegar al tope de 10 000).

### RF9 — Procedimientos almacenados
`POST /api/procedimientos/ejecutarsp` con body `{nombreSP, ...parámetros}`.
Ejecuta el SP en el motor activo (CALL/EXEC según dialecto) y devuelve
`{Procedimiento, Resultados, Total, Mensaje}`.

### RF10 — Estructuras y diagnóstico
- `GET /api/estructuras/{tabla}/modelo` → columnas, tipos y restricciones.
- `GET /api/estructuras/basedatos` → tablas, vistas, funciones, SPs, triggers.
- `GET /api/diagnostico/conexion` → BD, versión del motor, servidor, hora de
  inicio, usuario conectado (sin credenciales).
- `GET /` y `GET /api/info` → bienvenida y ayuda de uso.

### RF11 — Selección de motor por configuración
`DatabaseProvider` decide el motor: `postgres`, `mariadb`/`mysql`,
`sqlserver` (alias `sqlserverexpress`, `localdb`; también el default). Las
cadenas viven en `ConnectionStrings` de `appsettings.json` y **pueden
sobrescribirse por variables de entorno** (`DatabaseProvider`,
`ConnectionStrings__Postgres`, …) — la vía natural para inyectar valores al
correr en contenedores.

## 4. Requisitos no funcionales

- **RNF1 — Asíncrona:** todo el acceso a datos con `async/await` (ADO.NET async).
- **RNF2 — Errores uniformes:** `{estado, mensaje, detalle, ...contexto}` con
  400/401/403/404/500 según la tabla de la constitución (Artículo 6).
- **RNF3 — CORS abierto** (política `PermitirTodo`).
- **RNF4 — Swagger en `/swagger`** con botón **Authorize** (esquema Bearer) y
  ReDoc en `/redoc`.
- **RNF5 — Serialización segura:** `DBNull` → `null`; nombres de columna en
  minúsculas en consultas/SPs; `JsonElement` del body → tipos nativos .NET.
- **RNF6 — Contenedor Docker:** puerto **8013**, imagen `dotnet/sdk:10.0` con
  `dotnet watch` (guardar un `.cs` recompila y reinicia solo).
- **RNF7 — Logging estructurado** (`ILogger`) en cada fase: inicio, éxito,
  sin-datos, validación, acceso denegado, error crítico.

## 5. Criterios de aceptación

1. La API arranca (Docker o `dotnet run`) y `GET http://localhost:8013/`
   responde la bienvenida; `/swagger` y `/redoc` abren.
2. `GET /api/producto` **sin token → 401**; con token Bearer → los 8 productos
   con envoltura `{tabla, esquema, limite, total, datos}`.
3. `POST /api/Autenticacion/token` con `admin@correo.com` / `admin123` sobre la
   tabla `usuario` → 200 con token; con contraseña mala → 401.
4. `GET /api/factura/numero/1` (sin token) devuelve la factura 1 — conversión
   texto→entero automática.
5. Ciclo CRUD sobre `persona` (POST → PUT → GET por clave → DELETE) responde
   200/200/200/200 y 404 con clave inexistente.
6. `POST /api/usuario?camposEncriptar=contrasena` guarda hash BCrypt de 60
   caracteres; `verificar-contrasena` responde 200 con la original y 401 con otra.
7. `POST /api/consultas/ejecutarconsultaparametrizada` con
   `SELECT * FROM producto WHERE stock > @minimo` y `{"minimo": 20}` devuelve
   solo los productos con stock > 20; una tabla en `TablasProhibidas` → 403;
   un `DELETE ...` → rechazado.
8. `POST /api/procedimientos/ejecutarsp` ejecuta un SP de bdfacturas y devuelve
   sus filas.
9. Repetir 2–8 con `DatabaseProvider=mariadb` y `=sqlserver`: comportamiento
   idéntico sin cambiar código.

## 6. Glosario

| Término | Significado |
|---|---|
| Repositorio | Clase que habla SQL con UN motor concreto (lectura o consultas) |
| Servicio | Lógica de negocio + política de tablas, ignorante del motor |
| Proveedor (provider) | Motor activo (`postgres`, `mariadb`, `sqlserver`) |
| "Fábrica" | El `switch` de registro en `Program.cs`: el contenedor DI elige la clase según el proveedor |
| Contrato / interfaz | `interface` C# que define QUÉ métodos debe tener una clase |
| JWT | Token firmado (HS256) que el cliente presenta como `Authorization: Bearer …` |
