# Investigación y decisiones — API Genérica C# (ASP.NET Core)

> **Documento 4 de 8** del spec kit · **Lectura opcional** (contexto de por qué
> el plan es como es). Cada decisión con sus alternativas y justificación.

---

## D1 — ¿Por qué una API "genérica"?
**Decisión:** endpoints parametrizados por nombre de tabla (`/api/{tabla}`),
con las filas viajando como `Dictionary<string, object?>`.
**Por qué:** demuestra que un CRUD es una operación uniforme — una sola
implementación sirve para las 12 tablas de la BD de prueba y para cualquier
otra. **Precio asumido:** sin validación por entidad (un body con columnas
inventadas llega hasta la BD y falla allá) y superficie genérica difícil de
asegurar — aceptable en contexto docente; en producción exigiría al menos una
lista blanca de tablas (aquí existe su inversa: `TablasProhibidas`).

## D2 — Dapper + ADO.NET en vez de Entity Framework
EF Core exige modelos por tabla — lo contrario de la genericidad. Dapper deja
el SQL visible (objetivo docente) y mapea a `Dictionary<string, object?>` sin
esfuerzo. Por debajo, ADO.NET async con los tres drivers oficiales: Npgsql,
MySqlConnector y Microsoft.Data.SqlClient (este último habla TDS nativo — no
hay que instalar ODBC ni ningún driver del sistema operativo).

## D3 — El contenedor DI como fábrica
**Alternativas:** una clase Factory propia que instancie repositorios por
petición, o un `IServiceProvider` consultado a mano. **Decisión:** el
`switch (DatabaseProvider)` en `Program.cs` registra la implementación concreta
y el contenedor la inyecta (`AddScoped`) donde se pida la interfaz. Mismo
principio abierto/cerrado, mecanismo idiomático del framework y cero código de
infraestructura propio. Precio: cambiar de proveedor exige reiniciar el proceso
(el `switch` corre al arrancar) — asumido y documentado.

## D4 — Dos familias de repositorio (Lectura y Consultas)
El CRUD genérico devuelve `List<Dictionary<…>>`; las consultas libres y los SPs
devuelven `DataTable` (columnas desconocidas + parámetros OUT). Separarlos en
`IRepositorioLecturaTabla` e `IRepositorioConsultas` mantiene interfaces
pequeñas (ISP) — el precio son 6 clases concretas en vez de 3, asumido.

## D5 — JWT real, pero en un solo endpoint
**Decisión:** `POST /api/Autenticacion/token` emite JWT (verificando BCrypt
contra cualquier tabla de usuarios) y solo `GET /api/{tabla}` exige
`[Authorize]`. **Por qué:** un endpoint protegido basta para experimentar el
ciclo completo 401 → token → 200 en Swagger, sin convertir cada demo de clase
en una sesión de gestión de tokens. Producción real protegería todo y firmaría
con secreto rotado — está documentado como límite del alcance.

## D6 — Consultas libres pero SELECT-only con lista negra
`/api/consultas` acepta SQL arbitrario del cliente — un riesgo evidente.
Mitigación en el servicio: solo sentencias **SELECT**, parámetros `@nombrados`
obligatorios, tope de 10 000 filas y política `TablasProhibidas` (403).
**Alternativa rechazada:** lista blanca de consultas predefinidas — mata el
valor didáctico de experimentar con SQL desde Swagger.

## D7 — BCrypt.Net-Next con costo 10
Hash estándar BCrypt (`$2a$`/`$2b$`, 60 caracteres) — interoperable con
cualquier otra pila que use BCrypt contra la misma BD. Costo 10: hardware
docente; la diferencia de seguridad frente a costos mayores es irrelevante en
este contexto. La encriptación ocurre en el **repositorio** (es parte de "cómo
se persiste", y así el servicio queda igual para todos los motores); la
verificación vive en el **servicio** (es regla de negocio: 200/401/404).

## D8 — `JsonElement` → tipos nativos en el controller
System.Text.Json deserializa el body a `JsonElement`, que los drivers SQL no
aceptan como parámetro. El helper `ConvertirJsonElement` (switch sobre
`ValueKind`) convierte a `string`/`int`/`double`/`bool`/`null` **antes** de
llegar al servicio. La dirección inversa (valor de URL → tipo real de la
columna) la resuelve cada repositorio consultando el catálogo del motor, con el
caso especial `YYYY-MM-DD` sobre columna fecha/hora → `CAST(col AS DATE)`.

## D9 — DataTable y columnas en minúsculas
Consultas y SPs devuelven `DataTable` que el controller aplana a
`List<Dictionary<…>>` con claves en minúsculas. **Por qué minúsculas:** cada
motor devuelve el caso que quiere (Oracle grita en mayúsculas); normalizar da
respuestas idénticas entre motores — el contrato de esta API es que el motor no
se note.

## D10 — Swagger en `/swagger` + ReDoc, con esquema Bearer
Swashbuckle publica la UI interactiva en `/swagger` con
`AddSecurityDefinition("Bearer")` para el botón **Authorize** (probar el JWT
sin salir del navegador). ReDoc en `/redoc` da la vista de solo lectura.
OpenAPI en `/swagger/v1/swagger.json`.

## D11 — dotnet watch en la imagen SDK (no multi-stage runtime)
**Alternativa clásica:** build multi-stage → imagen runtime pequeña.
**Decisión:** imagen SDK + `dotnet watch` + código montado como volumen, porque
la regla de este entorno es "guardar recarga sin rebuild": los estudiantes
editan el código en caliente. Precio: imagen grande y arranque más lento —
irrelevante en un entorno docente local. `DOTNET_USE_POLLING_FILE_WATCHER=true`
porque los eventos de archivo no cruzan el volumen desde Windows.
