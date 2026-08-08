# Constitución — Front Blazor (Blazor Server)

> **Documento 1 de 8** del spec kit. Orden de lectura:
> `1_constitution → 2_spec → 3_plan → 4_research → 5_data_model → 6_contracts → 7_quickstart → 8_tasks`.
>
> Principios innegociables de este proyecto. El spec kit es **autocontenido**:
> con esta carpeta se reconstruye el front completo desde cero, sin depender de
> ningún otro proyecto o documento externo (los contratos de la API que consume
> están descritos en el propio kit, en 6_contracts.md).
>
> Nota: la carpeta `sdd/` del proyecto conserva la documentación SDD **original**
> con la que se construyó este front (constitución, especificación, clarificación,
> plan y tareas al estilo GitHub Spec-Kit). Este kit es su versión normalizada.

---

## Artículo 1 — Propósito didáctico

Proyecto para enseñar a construir un **frontend web completo en C#** que consume
una API REST: CRUD sobre 10+ tablas, **login con JWT**, **control de acceso por
roles y rutas**, y facturación maestro-detalle. Claridad sobre sofisticación:

- Código y comentarios en **español**, con intención de tutorial (los documentos
  `Paso1..12*.md` del proyecto narran su construcción).
- Un solo lenguaje en todo el proyecto: la lógica es C#; **prohibido JavaScript
  para lógica de negocio**.

## Artículo 2 — El front nunca toca la base de datos

- CERO drivers de BD y CERO Entity Framework: **todo** pasa por HTTP hacia una
  API REST genérica (contratos en 6_contracts.md §2).
- Las PKs y FKs **se descubren en runtime** vía `GET /api/estructuras/basedatos`
  — prohibido hardcodear nombres de columnas clave.
- La URL de la API va en configuración (`ApiBaseUrl` en `appsettings.json`,
  sobrescribible por variable de entorno), jamás en el código.

## Artículo 3 — Arquitectura Blazor Server en capas

```
Navegador ←SignalR→ BLAZOR SERVER
                      ├── Components/Pages/   (UI: una página .razor por tabla)
                      ├── Components/Layout/  (MainLayout: sesión + control de acceso)
                      └── Services/           (ApiService · AuthService · SpService)
                            │ HTTP + Authorization: Bearer {JWT}
                            ▼
                      API REST genérica (:8013)
```

- El navegador **no ejecuta C#**: el servidor renderiza y los eventos viajan por
  SignalR (`@rendermode InteractiveServer` global en `App.razor`).
- Las páginas solo conocen a los **servicios** (inyectados con `@inject`);
  los servicios son los únicos que hablan HTTP.

## Artículo 4 — Seguridad en 3 capas obligatorias

| Capa | Dónde | Qué protege | Cómo |
|---|---|---|---|
| **BCrypt** | BD (vía API) | Contraseñas | `?camposEncriptar=contrasena` al crear/actualizar |
| **JWT** | API | Datos del backend | `ApiService.AgregarTokenJwt()` en cada petición |
| **Sesión** | Front (`ProtectedSessionStorage`) | Páginas | `MainLayout` verifica en `OnAfterRenderAsync` + `LocationChanged` |

El control de acceso es **por datos, no por código**: los roles del usuario y
las rutas permitidas por rol viven en la BD (`rol_usuario`, `rutarol`) y se
verifican en **cada navegación**.

## Artículo 5 — Prohibiciones

| Prohibido | Razón |
|---|---|
| Acceder a la BD directamente / Entity Framework | Todo va por la API REST |
| Hardcodear URLs de la API o nombres de PK/FK | Configuración y descubrimiento dinámico |
| Contraseñas en texto plano | BCrypt obligatorio (vía API) |
| `localStorage` para la sesión | Solo `ProtectedSessionStorage` (encriptada) |
| JavaScript para lógica de negocio | La lógica vive en C# (servicios) |

## Artículo 6 — Convenciones fijas

| Cosa | Convención |
|---|---|
| Puerto | **8014** |
| Nombres | PascalCase para clases/métodos/archivos `.razor`; rutas URL en `minusculas-guiones` (`/cambiar-contrasena`) |
| Estructura | `Components/Pages/` (una página por tabla) · `Components/Layout/` · `Services/` |
| Patrón CRUD | Cada `{Tabla}.razor`: `@page "/{tabla}"` + `@inject ApiService` + listar/crear/editar/eliminar |
| UI | Bootstrap 5 local (en `wwwroot/lib/`), sidebar oscuro con `NavMenu`, mensajes de éxito/error tras cada operación |
| Login | `EmptyLayout` (sin sidebar); el resto de páginas bajo `MainLayout` |
