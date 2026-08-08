# Plan técnico — API Genérica C# (ASP.NET Core)

> **Documento 3 de 8** del spec kit: **CÓMO** construir lo especificado en
> [2_spec.md](2_spec.md). El porqué de cada decisión: [4_research.md](4_research.md) ·
> endpoints exactos: [6_contracts.md](6_contracts.md) · orden de trabajo: [8_tasks.md](8_tasks.md).

---

## 1. Stack

| Pieza | Elección | Por qué |
|---|---|---|
| Lenguaje / runtime | C# sobre **.NET 10** | Imagen `mcr.microsoft.com/dotnet/sdk:10.0` |
| Framework web | ASP.NET Core (controllers) | DI integrada, `[Authorize]`, Swagger vía Swashbuckle |
| Acceso a datos | **Dapper** + ADO.NET async | SQL visible; sin modelos por tabla (lo contrario de EF) |
| Driver PostgreSQL | Npgsql | Estándar de facto |
| Driver MySQL/MariaDB | MySqlConnector | Async real, MIT |
| Driver SQL Server | Microsoft.Data.SqlClient | Oficial; habla TDS nativo, sin dependencias del sistema operativo |
| Contraseñas | BCrypt.Net-Next | Hash de 60 caracteres, costo 10 |
| Autenticación | Microsoft.AspNetCore.Authentication.JwtBearer | Tokens HS256 validados por middleware |
| Documentación | Swashbuckle.AspNetCore + Swashbuckle.AspNetCore.ReDoc | `/swagger` con botón Authorize, `/redoc` |
| Configuración | `IConfiguration` (appsettings.json + variables de entorno) | Las env vars **sobrescriben** el JSON: así inyecta valores el compose |

## 2. Estructura de carpetas

```
api_generica_csharp/
├── Dockerfile                    # dotnet/sdk:10.0 + dotnet watch (puerto 8013)
├── ApiGenericaCsharp.csproj      # net10.0 + paquetes del stack
├── Program.cs                    # DI, JWT, CORS, Swagger/ReDoc, switch de proveedor
├── appsettings.json              # DatabaseProvider, ConnectionStrings, Jwt, TablasProhibidas
├── Modelos/
│   └── ConfiguracionJwt.cs       # Key, Issuer, Audience, DuracionMinutos (bind de "Jwt")
├── Controllers/
│   ├── EntidadesController.cs        # CRUD /api/{tabla} + /api/info + / + verificar-contrasena
│   ├── AutenticacionController.cs    # POST /api/Autenticacion/token (emite JWT)
│   ├── ConsultasController.cs        # POST /api/consultas/ejecutarconsultaparametrizada
│   ├── ProcedimientosController.cs   # POST /api/procedimientos/ejecutarsp
│   ├── EstructurasController.cs      # GET /api/estructuras/{tabla}/modelo · /basedatos
│   └── DiagnosticoController.cs      # GET /api/diagnostico/conexion
├── Servicios/
│   ├── Abstracciones/
│   │   ├── IProveedorConexion.cs         # ProveedorActual, ObtenerCadenaConexion()
│   │   ├── IServicioCrud.cs              # Listar/PorClave/Crear/Actualizar/Eliminar/VerificarContrasena
│   │   ├── IServicioConsultas.cs         # consultas parametrizadas + SPs
│   │   └── IPoliticaTablasProhibidas.cs  # ¿esta tabla se puede tocar?
│   ├── Conexion/ProveedorConexion.cs     # lee DatabaseProvider y su ConnectionString
│   ├── Politicas/PoliticaTablasProhibidasDesdeJson.cs  # lee "TablasProhibidas"
│   ├── Utilidades/EncriptacionBCrypt.cs  # Encriptar(valor, costo) / Verificar(valor, hash)
│   ├── ServicioCrud.cs                   # reglas de negocio + política de tablas
│   └── ServicioConsultas.cs              # valida SELECT-only + tablas prohibidas
└── Repositorios/
    ├── Abstracciones/
    │   ├── IRepositorioLecturaTabla.cs   # 6 métodos CRUD + diagnóstico
    │   └── IRepositorioConsultas.cs      # consultas, SPs y metadatos (DataTable)
    ├── RepositorioLecturaPostgreSQL.cs   ├── RepositorioConsultasPostgreSQL.cs
    ├── RepositorioLecturaMysqlMariaDB.cs ├── RepositorioConsultasMysqlMariaDB.cs
    └── RepositorioLecturaSqlServer.cs    └── RepositorioConsultasSqlServer.cs
```

## 3. Arquitectura en capas (flujo de una petición)

```
HTTP → Controller (valida forma, [Authorize] donde aplique, traduce excepciones a HTTP)
     → IServicioCrud / IServicioConsultas (reglas de negocio, política de tablas)
     → IRepositorioLecturaTabla / IRepositorioConsultas (SQL del dialecto activo)
     → driver ADO.NET (Npgsql / MySqlConnector / SqlClient) → base de datos
```

**Regla de dependencias:** el controller solo conoce interfaces de servicio; el
servicio solo conoce interfaces de repositorio; **solo `Program.cs` conoce las
clases concretas** (inversión de dependencias con el contenedor DI).

## 4. Decisiones de diseño clave

### 4.1 La "fábrica" es el contenedor DI
El patrón Factory se implementa como un `switch` de registro en `Program.cs`:
según el proveedor configurado, se registra en el contenedor la implementación
concreta de cada interfaz de repositorio:

```csharp
var proveedorBD = builder.Configuration.GetValue<string>("DatabaseProvider") ?? "SqlServer";
switch (proveedorBD.ToLower())
{
    case "postgres":
        builder.Services.AddScoped<IRepositorioLecturaTabla, RepositorioLecturaPostgreSQL>();
        builder.Services.AddScoped<IRepositorioConsultas,   RepositorioConsultasPostgreSQL>();
        break;
    case "mariadb": case "mysql":            /* MysqlMariaDB */ break;
    case "sqlserver": case "sqlserverexpress": case "localdb": default: /* SqlServer */ break;
}
```

Agregar un motor = 2 repositorios + 1 `case` (abierto/cerrado). El contenedor
resuelve la clase concreta una vez por request (`AddScoped`); el `switch` corre
una sola vez, al arrancar.

### 4.2 Configuración con `IConfiguration`
- `appsettings.json`: `DatabaseProvider`, `ConnectionStrings:{Postgres,MariaDB,SqlServer}`,
  `Jwt:{Key,Issuer,Audience,DuracionMinutos}`, `TablasProhibidas: []`.
- Las **variables de entorno sobrescriben el JSON** con la convención `__`:
  `ConnectionStrings__Postgres`, `DatabaseProvider`. Es la vía para inyectar
  configuración al correr en contenedores (p. ej. hosts internos de una red
  Docker en lugar de `localhost`).
- `ProveedorConexion` (Singleton) lee ambos valores y entrega la cadena del
  proveedor activo con mensajes de error claros; la búsqueda de claves es
  case-insensitive (`postgres` encuentra `Postgres`).

### 4.3 SQL genérico: mismo algoritmo, dialecto distinto

| Aspecto | PostgreSQL | MySQL/MariaDB | SQL Server |
|---|---|---|---|
| Comillas de identificador | `"tabla"` | `` `tabla` `` | `[tabla]` |
| Limitar filas | `LIMIT @limite` | `LIMIT @limite` | `SELECT TOP (n)` |
| Esquema por defecto | `public` | la BD misma (no antepone) | `dbo` |
| SPs | `CALL` / `SELECT funcion()` | `CALL` | `EXEC` |
| Diagnóstico | `current_database()`, `pg_postmaster_start_time()` | `DATABASE()`, `VERSION()` | `DB_NAME()`, `@@VERSION` |

Métodos del repositorio de lectura: `ObtenerFilasAsync` (límite default 1000),
`ObtenerPorClaveAsync` (con `CAST(col AS DATE)` si el valor es fecha sin hora),
`CrearAsync`, `ActualizarAsync`, `EliminarAsync`, `ObtenerHashContrasenaAsync`,
`ObtenerDiagnosticoConexionAsync`. **Siempre parámetros `@nombrados`**, nunca
concatenar valores.

### 4.4 Conversión JSON → tipos nativos
ASP.NET deserializa el body a `JsonElement`; el helper `ConvertirJsonElement`
(pattern matching sobre `ValueKind`) lo pasa a `string`/`int`/`double`/`bool`/
`null` antes de armar parámetros SQL. En la salida, `DBNull.Value` → `null` y
los nombres de columna de consultas/SPs se normalizan a minúsculas.

### 4.5 JWT de extremo a extremo
- `ConfiguracionJwt` se llena con `builder.Configuration.GetSection("Jwt")`.
- `AddAuthentication(JwtBearer)` valida issuer, audience, expiración y firma
  (clave simétrica ≥ 32 caracteres, HS256).
- `AutenticacionController` reutiliza `IServicioCrud.VerificarContrasenaAsync`
  (BCrypt) y, si es 200, emite el token con claims `Name`, `tabla`, `campoUsuario`
  y expiración de `DuracionMinutos` (60).
- Solo `GET /api/{tabla}` lleva `[Authorize]`; el resto `[AllowAnonymous]` —
  decisión didáctica: un endpoint protegido basta para ver el 401 → token → 200.
- Swagger define el esquema Bearer para probarlo con el botón **Authorize**.

### 4.6 Política de tablas prohibidas
`IPoliticaTablasProhibidas` (Singleton) lee `TablasProhibidas` del JSON.
`ServicioCrud` y `ServicioConsultas` la consultan antes de tocar la BD; una
tabla vetada lanza `UnauthorizedAccessException` → 403. Con la lista vacía
(default del proyecto) todo pasa.

### 4.7 Traducción de excepciones a HTTP (en el controller)
| Excepción C# | HTTP |
|---|---|
| `ArgumentException` | 400 |
| `UnauthorizedAccessException` (política de tablas) | 403 |
| `InvalidOperationException` | 404 en lecturas · 500 en escrituras |
| cualquier otra | 500 (con tipo, mensaje e inner exception en `detalle`) |

Además el middleware JWT responde 401 solo ante `[Authorize]` sin token válido.

### 4.8 Program.cs (pipeline)
CORS `PermitirTodo` → sesión (cache en memoria) → Swagger/SwaggerUI (`/swagger`)
→ ReDoc (`/redoc`) → `UseHttpsRedirection` (inofensivo en Docker: solo HTTP) →
`UseAuthentication` → `UseAuthorization` → `MapControllers`.

## 5. Dockerfile

1. `FROM mcr.microsoft.com/dotnet/sdk:10.0` — la imagen **SDK**, no runtime,
   porque el contenedor corre `dotnet watch` (guardar un `.cs` recompila y
   reinicia solo, sin rebuild de imagen).
2. `COPY ApiGenericaCsharp.csproj` + `dotnet restore` **antes** del resto del
   código (caché de capas).
3. `ENV DOTNET_USE_POLLING_FILE_WATCHER=true` (los volúmenes desde Windows no
   emiten eventos de archivo) · `ASPNETCORE_URLS=http://0.0.0.0:8013`.
4. `CMD dotnet watch --project ApiGenericaCsharp.csproj run --no-launch-profile`.
5. Si se orquesta con docker-compose: montar el código en `/app` y dejar
   `bin/`+`obj/` en volúmenes anónimos de Linux, para que los compilados del
   contenedor no se mezclen con los del host Windows.

## 6. Convenciones

- Todo en **español**: clases, métodos, comentarios y mensajes.
- Comentarios con intención de tutorial: encabezado por archivo con su papel y
  los principios SOLID aplicados; XML-docs (`///`) en los endpoints.
- PascalCase para clases/métodos/carpetas, prefijo `I` para interfaces.
