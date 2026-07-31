# Plan técnico — Front Blazor (Blazor Server)

> **Documento 3 de 8** del spec kit: **CÓMO** construir lo especificado en
> [2_spec.md](2_spec.md). El porqué de cada decisión: [4_research.md](4_research.md) ·
> contratos exactos: [6_contracts.md](6_contracts.md) · orden de trabajo: [8_tasks.md](8_tasks.md).

---

## 1. Stack

| Pieza | Elección | Por qué |
|---|---|---|
| Lenguaje / runtime | C# sobre **.NET 10** | Un solo lenguaje en todo el proyecto |
| Framework | **Blazor Server** (Razor Components interactivos) | El C# corre en el servidor; el navegador solo pinta (SignalR) |
| HTTP | `HttpClient` inyectado por DI | Nativo de .NET, async, sin dependencias extra |
| Sesión | `ProtectedSessionStorage` | sessionStorage encriptado con Data Protection del servidor |
| CSS | Bootstrap 5 **local** (`wwwroot/lib/bootstrap/`) | Viene con la plantilla Blazor; sin npm ni CDN |
| Correo | `System.Net.Mail.SmtpClient` | Para recuperar contraseña; credenciales por configuración |
| Sin paquetes NuGet adicionales | — | Todo lo necesario está en el framework |

## 2. Estructura de carpetas

```
front_blazor/
├── Dockerfile                    # dotnet/sdk:10.0 + dotnet watch (puerto 8004)
├── FrontBlazorTutorial.csproj    # net10.0, sin paquetes externos
├── Program.cs                    # DI: HttpClient(ApiBaseUrl) + AuthService + ApiService + SpService
├── appsettings.json              # ApiBaseUrl + Smtp (sin credenciales; ver 6_contracts §4)
├── Services/
│   ├── ApiService.cs             # CRUD genérico HTTP + AgregarTokenJwt()
│   ├── AuthService.cs            # Login, sesión, roles/rutas, estructura, contraseñas
│   └── SpService.cs              # Ejecución de procedimientos almacenados vía API
├── Components/
│   ├── App.razor                 # <Routes @rendermode="InteractiveServer" />
│   ├── Routes.razor              # Router de Blazor
│   ├── Layout/
│   │   ├── MainLayout.razor      # Sidebar + top-row + sesión + control de acceso
│   │   ├── NavMenu.razor         # Menú lateral (un NavLink por tabla)
│   │   └── EmptyLayout.razor     # Layout vacío (login y páginas de auth)
│   └── Pages/
│       ├── Home.razor            # @page "/"
│       ├── Login.razor           # @page "/login" (EmptyLayout)
│       ├── Producto.razor …      # un CRUD por tabla: /producto /persona /usuario
│       │                         #   /empresa /rol /ruta /cliente /vendedor
│       ├── Factura.razor         # maestro-detalle
│       ├── CambiarContrasena.razor · RecuperarContrasena.razor · SinAcceso.razor
│       └── Error.razor
├── wwwroot/                      # app.css + Bootstrap local
├── script_bd/                    # bdfacturas para PostgreSQL y SQL Server (BD de prueba)
├── sdd/                          # Documentación SDD original (Spec-Kit real del proyecto)
└── Paso0..12*.md                 # Tutorial paso a paso de la construcción
```

## 3. Flujo de una petición (crear un producto)

```
clic "Crear" (navegador) → SignalR → Producto.razor (servidor)
    → ApiService.CrearAsync("producto", datos)
    → AgregarTokenJwt()  — header Authorization: Bearer {token}
    → POST {ApiBaseUrl}/api/producto  (HttpClient)
    ← 200 {estado, mensaje}
    → mensaje verde + recargar tabla → SignalR repinta el DOM
```

**Regla de dependencias:** las páginas solo conocen a los servicios
(`@inject`); solo los servicios usan `HttpClient`; solo `Program.cs` sabe
construirlos (inversión de dependencias con el contenedor DI).

## 4. Decisiones de diseño clave

### 4.1 Los tres servicios
- **`ApiService`** — fachada CRUD: `ListarAsync`, `CrearAsync`,
  `ActualizarAsync`, `EliminarAsync` + `AgregarTokenJwt()` antes de cada
  llamada. Recibe `HttpClient` (con `BaseAddress = ApiBaseUrl`) y `AuthService`
  (para leer el token) por constructor.
- **`AuthService`** — todo lo de identidad: `Login()` (token + roles + rutas +
  guardar sesión), `Restaurar()` (leer sesión tras F5), `TieneAcceso(ruta)`,
  `CambiarContrasena()`, `RecuperarContrasena()` (SMTP), `Logout()`. Además
  `PrecargarEstructura()`: descubre y cachea PKs/FKs de la BD vía la API.
- **`SpService`** — ejecutar procedimientos almacenados vía la API (facturación).

Registro en `Program.cs`: **`AddScoped` los tres** (una instancia por circuito
SignalR = por usuario; un Singleton compartiría el token entre usuarios).

### 4.2 Roles y rutas con UNA consulta (y plan B)
`CargarDatosRolesYRutas()` envía **un solo SQL con JOINs** (usuario →
rol_usuario → rol → rutarol → ruta) al endpoint de consultas parametrizadas de
la API: solo viajan las filas del usuario. Si ese endpoint no existe en la API,
**fallback** automático a GETs por tabla filtrando en C# (más tráfico, mismo
resultado) — patrón Strategy.

### 4.3 Control de acceso en el Layout (no hay middleware)
Blazor Server navega por SignalR, sin peticiones HTTP por página — no existe el
middleware clásico. El guardián es `MainLayout`:

1. `OnAfterRenderAsync(firstRender)` — restaura la sesión (necesita JavaScript,
   por eso NO en `OnInitializedAsync`), redirige a `/login` si no hay, fuerza
   `/cambiar-contrasena` si está marcado, y verifica la ruta actual.
2. `LocationChanged` — en **cada** navegación llama `VerificarAcceso()`:
   rutas públicas pasan; sin permiso → `/sin-acceso`.
3. `IDisposable.Dispose()` — desuscribe el evento (evita memory leak).
4. Spinner mientras restaura (`_cargando`) para que no "parpadee" contenido
   protegido antes del redirect.

### 4.4 Sesión encriptada
`ProtectedSessionStorage` guarda usuario/token/roles/rutas **encriptados** con
Data Protection del servidor: el usuario no puede leerlos ni inyectar roles
desde la consola del navegador; un byte alterado invalida la sesión. Sobrevive
a F5, muere al cerrar la pestaña.

### 4.5 Formularios CRUD
Formulario compartido crear/editar con la PK deshabilitada al editar; campos FK
como `<select>` cargados con `ListarAsync(tablaPadre)`; tipos de input HTML
acordes al dato (`number`, `email`, …). Eliminar siempre con confirmación.

### 4.6 Configuración
`IConfiguration` lee `appsettings.json` y **las variables de entorno lo
sobrescriben** (convención `__`): `ApiBaseUrl`, `Smtp__User`, `Smtp__Pass`.
El repositorio NUNCA contiene credenciales SMTP reales.

## 5. Dockerfile

1. `FROM mcr.microsoft.com/dotnet/sdk:10.0` — imagen **SDK**, no runtime,
   porque corre `dotnet watch` (guardar un `.razor` recompila y reinicia solo).
2. `COPY *.csproj` + `dotnet restore` antes del resto (caché de capas).
3. `ENV DOTNET_USE_POLLING_FILE_WATCHER=true` (volúmenes desde Windows no
   emiten eventos) · `ASPNETCORE_URLS=http://0.0.0.0:8004`.
4. `CMD dotnet watch --project FrontBlazorTutorial.csproj run --no-launch-profile`.
5. Si se orquesta con docker-compose: código montado en `/app`, `bin/`+`obj/`
   en volúmenes anónimos, y `ApiBaseUrl` apuntando al host interno de la API.

## 6. Convenciones

- Todo en **español**: nombres, comentarios y mensajes al usuario.
- PascalCase para clases/métodos/archivos; rutas URL en `minusculas-guiones`.
- Cada página CRUD sigue el mismo esqueleto (ver Artículo 6 de la constitución) —
  agregar una tabla nueva = un `.razor` nuevo + un NavLink, sin tocar lo demás.
