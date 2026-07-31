# Investigación y decisiones — Front Blazor (Blazor Server)

> **Documento 4 de 8** del spec kit · **Lectura opcional** (contexto de por qué
> el plan es como es). Cada decisión con sus alternativas y justificación.
> La carpeta `sdd/03_clarificacion.md` del proyecto conserva la sesión original
> de preguntas y respuestas de la que salieron varias de estas decisiones.

---

## D1 — Blazor Server en vez de Blazor WebAssembly
**Decisión:** Blazor Server. **Por qué:** el C# corre en el servidor y el
navegador se actualiza por SignalR — el estudiante no necesita entender
compilación a WASM ni descarga de DLLs. Además `ProtectedSessionStorage`
(sesión encriptada) depende de Data Protection **del servidor**: con WASM todo
correría en el navegador y la sesión sería manipulable. **Precio:** requiere
conexión permanente (WebSocket); si el servidor cae, la UI se congela.

## D2 — Consumir API REST en vez de Entity Framework
El front **no** accede a la BD: aprende a consumir APIs (el escenario real de
frontends desacoplados y microservicios). EF enseñaría ORM pero acoplaría el
front a la BD y duplicaría la lógica que ya vive en la API. Mismo argumento
para RestSharp/Refit: `HttpClient` nativo basta y no agrega dependencias.

## D3 — `ProtectedSessionStorage` en vez de localStorage o cookies
Encripta con Data Protection API antes de tocar el sessionStorage: inspeccionar
el almacenamiento del navegador muestra solo texto cifrado, y un byte alterado
invalida la sesión (no se pueden inyectar roles desde la consola). localStorage
guardaría token y roles legibles y manipulables. Semántica deseada de regalo:
sobrevive a F5, muere al cerrar la pestaña.

## D4 — Sesión y JWT son DOS capas, no una
La **sesión** protege las páginas del front (MainLayout redirige); el **JWT**
protege los datos de la API (sin token, Postman recibe 401 en los endpoints
`[Authorize]`). Quitar cualquiera deja un hueco: sin JWT, la API queda abierta
por fuera del front; sin sesión, cualquiera navega las páginas (aunque la API
le niegue los datos). Límite documentado: si el JWT expira, no hay refresh —
se vuelve a hacer login.

## D5 — Restaurar sesión en `OnAfterRenderAsync`, no en `OnInitializedAsync`
`ProtectedSessionStorage` necesita interop con JavaScript, y durante
`OnInitializedAsync` el componente aún no se renderizó (no hay JS): lanzaría
excepción. `OnAfterRenderAsync(firstRender)` corre con la conexión SignalR ya
viva. **Efecto secundario resuelto:** entre el primer render y la restauración
habría un "flash" de contenido — por eso el spinner `_cargando`.

## D6 — `LocationChanged` como guardián, porque no hay middleware
Blazor Server navega por SignalR sin peticiones HTTP por página: el middleware
clásico nunca ve esas "navegaciones". El equivalente es suscribirse a
`NavigationManager.LocationChanged` en `MainLayout` y verificar permisos en
cada cambio de URL (patrón Observer). Obliga a `IDisposable` para desuscribir
(memory leak si no).

## D7 — Roles y rutas con UNA consulta SQL (con fallback)
**Problema:** armar "qué rutas puede ver este usuario" toca 5 tablas.
**Decisión:** un solo SELECT con JOINs enviado al endpoint de consultas
parametrizadas de la API — la BD filtra y solo viajan las filas del usuario.
**Alternativa conservada como plan B (Strategy):** GETs por tabla filtrando en
C#, si la API no expone consultas. Con 1 000 usuarios, el plan B viaja 1 000
filas para quedarse con 1 — por eso es plan B.

## D8 — `AddScoped` para los servicios, jamás Singleton
En Blazor Server, Scoped = **una instancia por circuito SignalR** (por
usuario). Un Singleton compartiría UNA instancia — y por tanto el token JWT y
los roles — entre todos los usuarios conectados: un fallo de seguridad, no de
estilo.

## D9 — `@rendermode InteractiveServer` global (en App.razor)
Ponerlo por página es fácil de olvidar: una página sin él queda en SSR estático
— sin `@onclick`, sin sesión, sin SignalR — y "no funciona" sin error claro.
Global en `<Routes>` hace interactivas todas las páginas por defecto; el
tutorial gana previsibilidad a cambio de renunciar al render estático (que este
proyecto no necesita).

## D10 — Descubrimiento dinámico de PKs/FKs
Las URLs de actualizar/eliminar necesitan la columna clave
(`PUT /api/{tabla}/{pk}/{valor}`). Hardcodearla rompería el front ante
cualquier BD distinta. **Decisión:** al iniciar sesión se pide la estructura a
la API y se cachea (patrón Cache). Costo: una petición extra por login,
amortizada durante toda la sesión.

## D11 — Bootstrap local, no CDN
La plantilla de Blazor ya trae Bootstrap en `wwwroot/lib/` — usarlo hace al
front **autosuficiente sin internet** (aulas con red irregular) y con versiones
congeladas. Precio: ~2 MB versionados en el repo, asumido.

## D12 — dotnet watch en la imagen SDK (no multi-stage runtime)
**Decisión:** imagen SDK + código montado como volumen + `dotnet watch` =
guardar un `.razor` recompila y reinicia solo, sin rebuild de imagen — la regla
de este entorno es "guardar recarga sin rebuild". Producción usaría multi-stage
a imagen runtime — fuera del alcance (documentado en 2_spec §2).
`DOTNET_USE_POLLING_FILE_WATCHER=true` porque los eventos de archivo no cruzan
el volumen desde Windows.
