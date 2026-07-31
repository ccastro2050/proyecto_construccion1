# Tareas — Front Blazor (Blazor Server)

> **Documento 8 de 8** del spec kit: el orden de construcción. Cada fase termina
> en algo **verificable**. Requisitos: [2_spec.md](2_spec.md) · técnica:
> [3_plan.md](3_plan.md) · contratos: [6_contracts.md](6_contracts.md) ·
> validación final: [7_quickstart.md](7_quickstart.md).
>
> Prerrequisito: una API que cumpla [6_contracts.md](6_contracts.md) §2
> corriendo en `localhost:8003`, con la BD `bdfacturas` cargada.
> (El tutorial narrado de esta misma construcción está en `Paso0..12*.md`;
> `sdd/05_tareas.md` conserva el desglose original por estudiante y rama.)

---

## Fase 0 — Esqueleto
- [ ] `dotnet new blazor -n FrontBlazorTutorial` y fijar
      `<TargetFramework>net10.0</TargetFramework>` (sin paquetes NuGet extra).
- [ ] `appsettings.json` con `ApiBaseUrl` (`http://localhost:8003`) y sección
      `Smtp` **vacía** (las credenciales van por entorno).
- [ ] `.gitignore` (`bin/`, `obj/`, `.vs/`, `appsettings.Development.json`).

**Verificar:** `dotnet run` compila y sirve la plantilla vacía.

## Fase 1 — Cliente de la API
- [ ] `Program.cs`: `HttpClient` con `BaseAddress = ApiBaseUrl` (Scoped).
- [ ] `Services/ApiService.cs`: `ListarAsync`, `CrearAsync`, `ActualizarAsync`,
      `EliminarAsync` (contratos §2.1), captura de excepciones HTTP.
- [ ] Registrar `AddScoped<ApiService>()`.

**Verificar:** una página de prueba lista `producto` (aún sin token: contra un
endpoint anónimo de la API, o con `[Authorize]` desactivado temporalmente).

## Fase 2 — Layout y navegación
- [ ] `Components/App.razor`: `<Routes @rendermode="InteractiveServer" />`
      (global — ver [4_research.md](4_research.md) D9).
- [ ] `Components/Layout/MainLayout.razor` (sidebar + top-row + `@Body`),
      `NavMenu.razor` (un NavLink por tabla) y `EmptyLayout.razor` (vacío).
- [ ] `Components/Pages/Home.razor` (`@page "/"`).

**Verificar:** la app navega entre Home y páginas vacías con el sidebar.

## Fase 3 — Primer CRUD: Producto
- [ ] `Components/Pages/Producto.razor`: tabla + formulario crear/editar
      compartido (PK deshabilitada al editar) + eliminar con confirmación +
      mensajes de éxito/error. NavLink en el menú.

**Verificar:** ciclo completo crear→editar→eliminar sobre `producto`, visible
también en la BD.

## Fase 4 — CRUDs restantes (paralelizables)
- [ ] `Persona.razor`, `Usuario.razor`, `Empresa.razor`, `Rol.razor`,
      `Ruta.razor` — mismo esqueleto que Producto.
- [ ] `Cliente.razor` y `Vendedor.razor` — con `<select>` para sus FK
      (cargados con `ListarAsync` de la tabla padre).

**Verificar:** las 8 páginas CRUD funcionan; los selects muestran los registros
padre reales.

## Fase 5 — Factura maestro-detalle
- [ ] `Services/SpService.cs` (ejecutar SPs vía API, contratos §2.3).
- [ ] `Factura.razor`: lista + formulario con cabecera (selects de cliente y
      vendedor) y tabla dinámica de renglones (producto, cantidad) con
      agregar/quitar; crear cabecera + renglones contra la API **sin enviar
      totales** (los calcula el trigger de la BD).

**Verificar:** una factura de 2 renglones queda con subtotales/total correctos
en la BD y el stock descuenta.

## Fase 6 — Autenticación (el corazón del proyecto)
- [ ] `Services/AuthService.cs`: constructor con `ProtectedSessionStorage` +
      `IConfiguration`; `PrecargarEstructura()` (cachear PKs/FKs);
      `Login()` → token (§2.2) + roles y rutas con **1 SQL** vía consultas
      parametrizadas (con fallback a GETs — Strategy) + guardar sesión;
      `Restaurar()`, `TieneAcceso(ruta)`, `Logout()`.
- [ ] `ApiService.AgregarTokenJwt()` antes de cada llamada (header Bearer).
- [ ] Registrar `AddScoped<AuthService>()` y pasar `AuthService` a `ApiService`.
- [ ] `Login.razor` con `EmptyLayout`.

**Verificar:** login con `admin@correo.com`/`admin123` entra; con contraseña
mala muestra alerta; en F12→Network toda petición de datos lleva
`Authorization: Bearer`.

## Fase 7 — Guardián y páginas de contraseña
- [ ] `MainLayout`: `@implements IDisposable`; suscripción a `LocationChanged`
      en `OnInitialized`; `OnAfterRenderAsync` restaura sesión (+ spinner
      `_cargando`), redirige a `/login` o `/cambiar-contrasena` según el caso;
      `VerificarAcceso()` con rutas públicas y redirect a `/sin-acceso`;
      botón "Cerrar sesión".
- [ ] `CambiarContrasena.razor` (validación 6+/mayúscula/número; guarda con
      `?camposEncriptar=contrasena`), `RecuperarContrasena.razor` (SMTP desde
      configuración), `SinAcceso.razor` (403).

**Verificar:** los 9 puntos del recorrido de [7_quickstart.md](7_quickstart.md)
§3 pasan — incluye permisos por rol, F5, y URL prohibida a mano.

## Fase 8 — Docker y cierre
- [ ] `Dockerfile` según el plan (§5): sdk:10.0, restore cacheado, polling
      watcher, `dotnet watch` en el puerto 8004.
- [ ] `.dockerignore` (`bin/`, `obj/`, `.git/`, documentos).
- [ ] Opcional — orquestar con docker-compose: servicio en el puerto 8004 con
      el código montado como volumen, `bin/`+`obj/` en volúmenes anónimos, y
      `ApiBaseUrl` + `Smtp__*` inyectados por `environment:` (host interno de
      la API en lugar de `localhost`).

**Verificar:** [7_quickstart.md](7_quickstart.md) completo con el front en
Docker — equivale a los criterios de aceptación de [2_spec.md](2_spec.md) §5.
