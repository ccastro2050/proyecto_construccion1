# Tareas — API Genérica C# (ASP.NET Core)

> **Documento 8 de 8** del spec kit: el orden de construcción. Cada fase termina
> en algo **verificable**. Requisitos: [2_spec.md](2_spec.md) · técnica:
> [3_plan.md](3_plan.md) · endpoints: [6_contracts.md](6_contracts.md) ·
> validación final: [7_quickstart.md](7_quickstart.md).

---

## Fase 0 — Base de datos de prueba y esqueleto
- [ ] Montar la BD `bdfacturas` para probar contra ella
      ([5_data_model.md](5_data_model.md) §3).
- [ ] `dotnet new webapi -n ApiGenericaCsharp` (con controllers) y fijar
      `<TargetFramework>net10.0</TargetFramework>`.
- [ ] Agregar paquetes: `Dapper`, `Npgsql`, `MySqlConnector`,
      `Microsoft.Data.SqlClient`, `BCrypt.Net-Next`,
      `Microsoft.AspNetCore.Authentication.JwtBearer`, `Swashbuckle.AspNetCore`,
      `Swashbuckle.AspNetCore.ReDoc`.
- [ ] Crear carpetas `Controllers/`, `Modelos/`, `Servicios/` (`Abstracciones/`,
      `Conexion/`, `Politicas/`, `Utilidades/`), `Repositorios/` (`Abstracciones/`).

**Verificar:** `dotnet build` compila sin errores.

## Fase 1 — Configuración
- [ ] `appsettings.json`: secciones `DatabaseProvider`, `ConnectionStrings`
      (`Postgres`, `MariaDB`, `SqlServer` apuntando a los puertos donde se
      publicaron los motores en la Fase 0), `Jwt` (Key ≥ 32 caracteres, Issuer,
      Audience, DuracionMinutos) y `TablasProhibidas: []`.
- [ ] `Modelos/ConfiguracionJwt.cs` con las 4 propiedades.
- [ ] `Servicios/Abstracciones/IProveedorConexion.cs` y
      `Servicios/Conexion/ProveedorConexion.cs`: `ProveedorActual` (default
      `SqlServer`) y `ObtenerCadenaConexion()` con error claro si falta la clave.

**Verificar:** un test rápido en `Program.cs` imprime la cadena del proveedor
activo; con proveedor inexistente lanza `InvalidOperationException` descriptiva.

## Fase 2 — Contratos y utilidades
- [ ] `Repositorios/Abstracciones/IRepositorioLecturaTabla.cs` (6 métodos CRUD
      async + `ObtenerDiagnosticoConexionAsync`).
- [ ] `Repositorios/Abstracciones/IRepositorioConsultas.cs` (consulta
      parametrizada, validación, SP, y 3 métodos de metadatos).
- [ ] `Servicios/Abstracciones/IServicioCrud.cs`, `IServicioConsultas.cs`,
      `IPoliticaTablasProhibidas.cs`.
- [ ] `Servicios/Utilidades/EncriptacionBCrypt.cs`: `Encriptar(valor, costo=10)`
      y `Verificar(valor, hash)` (false ante cualquier excepción).
- [ ] `Servicios/Politicas/PoliticaTablasProhibidasDesdeJson.cs`.

**Verificar:** `Verificar("abc", Encriptar("abc"))` es `true`; la política con
`["usuario"]` en el JSON marca `usuario` como prohibida.

## Fase 3 — Primer repositorio: PostgreSQL
- [ ] `RepositorioLecturaPostgreSQL.cs`: identificadores `"entre comillas"`,
      esquema `public`, `LIMIT @limite` (default 1000), casteo del valor de URL
      según el catálogo, `CAST(col AS DATE)` para fechas sin hora, BCrypt en
      crear/actualizar si llega `camposEncriptar`, y diagnóstico
      (`current_database()`, `version()`, `pg_postmaster_start_time()`).

**Verificar:** un endpoint provisional (o test) lista `producto` y filtra
`factura` por `numero=1` contra la BD montada en la Fase 0.

## Fase 4 — Servicios
- [ ] `ServicioCrud.cs`: validaciones de entrada, consulta a la política de
      tablas (UnauthorizedAccessException → 403), delegación al repositorio,
      y `VerificarContrasenaAsync` que devuelve `(código, mensaje)` 200/404/401.
- [ ] `ServicioConsultas.cs`: SELECT-only, parámetros `@nombrados`, tope 10 000,
      tablas prohibidas, y ejecución de SPs.
- [ ] Registro en `Program.cs`: política (Singleton), proveedor (Singleton),
      servicios (Scoped) y el **switch por `DatabaseProvider`** que registra los
      repositorios PostgreSQL ([3_plan.md](3_plan.md) §4.1).

**Verificar:** con `DatabaseProvider=Postgres` el contenedor DI resuelve
`IServicioCrud` y lista una tabla.

## Fase 5 — Controllers CRUD + JWT
- [ ] `EntidadesController.cs`: los 6 endpoints de entidades + `/api/info` + `/`
      con el mapeo de excepciones del plan (§4.7), envolturas de
      [6_contracts.md](6_contracts.md), conversión `JsonElement`→nativo, y
      `[Authorize]` SOLO en `GET /api/{tabla}` (el resto `[AllowAnonymous]`).
- [ ] Configuración JWT en `Program.cs` (bind de `Jwt`, `AddAuthentication` +
      `AddJwtBearer` con validación completa) y Swagger con esquema Bearer.
- [ ] `AutenticacionController.cs`: `POST token` que verifica con
      `IServicioCrud` y emite el JWT (claims Name/tabla/campoUsuario).

**Verificar:** en `/swagger`: listar sin token → 401; pedir token con
`admin@correo.com`/`admin123`; Authorize; listar → 200. CRUD de `persona`
completo (200/200/200/200 y 404 con clave inexistente). Tabla vacía → 204.

## Fase 6 — Los otros dos motores
- [ ] `RepositorioLecturaMysqlMariaDB.cs`: backticks, sin esquema antepuesto,
      `LIMIT`; diagnóstico con `DATABASE()`/`VERSION()`.
- [ ] `RepositorioLecturaSqlServer.cs`: corchetes `[...]`, `TOP (n)`, esquema
      `dbo`; diagnóstico con `DB_NAME()`/`@@VERSION`.
- [ ] Completar los `case` del switch en `Program.cs`.

**Verificar:** repetir las pruebas de la Fase 5 con `DatabaseProvider=mariadb`
y `=sqlserver` — mismo comportamiento, sin cambiar código.

## Fase 7 — Consultas, SPs, estructuras y diagnóstico
- [ ] `RepositorioConsultas{PostgreSQL,MysqlMariaDB,SqlServer}.cs`: consulta
      parametrizada a `DataTable`, ejecución de SP (CALL/EXEC), esquema real de
      una tabla, estructura de tabla y estructura completa de la BD.
- [ ] `ConsultasController.cs`, `ProcedimientosController.cs`,
      `EstructurasController.cs`, `DiagnosticoController.cs` con los contratos
      de [6_contracts.md](6_contracts.md) §8–11 (columnas en minúsculas,
      `DBNull`→null).

**Verificar:** el SELECT parametrizado del quickstart §3.8 responde; un SP de
bdfacturas ejecuta; `/api/estructuras/producto/modelo` describe las 4 columnas;
`/api/diagnostico/conexion` muestra el motor activo.

## Fase 8 — Docker y cierre
- [ ] `Dockerfile` según el plan (§5): sdk:10.0, restore cacheado, polling
      watcher, `dotnet watch` en el puerto 8013.
- [ ] `.dockerignore` (`bin/`, `obj/`, `.git/`) y `.gitignore` (`bin/`, `obj/`, `.vs/`).
- [ ] Opcional — orquestar con docker-compose: servicio en el puerto 8013 con
      el código montado como volumen, volúmenes anónimos para `bin/`+`obj/`, y
      `DatabaseProvider` + `ConnectionStrings__*` inyectados por `environment:`
      (hosts internos de la red de compose en lugar de `localhost`).

**Verificar:** [7_quickstart.md](7_quickstart.md) completo con los 3 motores —
equivale a los criterios de aceptación de [2_spec.md](2_spec.md) §5, incluido
el cambio de motor y el ciclo JWT.
