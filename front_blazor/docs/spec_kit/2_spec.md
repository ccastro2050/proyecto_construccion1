# Especificación — Front Blazor (Blazor Server)

> **Documento 2 de 8** de un spec kit **autocontenido**: con esta carpeta se
> reconstruye el front completo desde cero, como proyecto independiente.
>
> | # | Documento | Contenido |
> |---|---|---|
> | 1 | [1_constitution.md](1_constitution.md) | Principios innegociables |
> | 2 | **2_spec.md** (este) | QUÉ construir: requisitos y criterios de aceptación |
> | 3 | [3_plan.md](3_plan.md) | CÓMO: stack, estructura, diseño de cada pieza |
> | 4 | [4_research.md](4_research.md) | Decisiones técnicas y alternativas *(lectura opcional)* |
> | 5 | [5_data_model.md](5_data_model.md) | Los datos que consume + la BD de prueba bdfacturas |
> | 6 | [6_contracts.md](6_contracts.md) | Rutas que expone + contratos de la API que consume |
> | 7 | [7_quickstart.md](7_quickstart.md) | Arranque y recorrido de validación |
> | 8 | [8_tasks.md](8_tasks.md) | Orden de construcción por fases verificables |

---

## 1. Propósito

Construir un **frontend web completo en Blazor Server (C# / .NET 10)** que
consume una API REST genérica: CRUD de 10+ tablas, **autenticación con JWT**
(verificación BCrypt del lado de la API), **control de acceso por roles y
rutas** verificado en cada navegación, gestión de contraseñas (cambiar y
recuperar por correo) y **facturación maestro-detalle**.

La idea central: el navegador nunca ejecuta lógica — Blazor Server renderiza en
el servidor y sincroniza por SignalR; el front nunca toca la BD — todo viaja
por HTTP con token Bearer hacia la API.

## 2. Alcance

**Incluye:**
- CRUD completo (listar, crear, editar, eliminar) para: producto, persona,
  usuario, empresa, rol, ruta, cliente, vendedor — con selects para las FK.
- Login (email + contraseña → JWT), logout, y sesión que sobrevive a F5 en
  `ProtectedSessionStorage` (encriptada).
- Control de acceso: roles del usuario y rutas permitidas por rol leídos de la
  BD; verificación en cada navegación; página 403 (`/sin-acceso`).
- Cambiar contraseña (validación: mínimo 6 caracteres, mayúscula y número) y
  recuperar contraseña (temporal por SMTP + cambio forzado al entrar).
- Factura maestro-detalle: cabecera (cliente, vendedor) + renglones dinámicos
  de producto/cantidad, creados contra la API.
- Descubrimiento dinámico de PKs/FKs vía la API (sin hardcodear columnas).

**No incluye:**
- La API REST ni la BD (existen aparte; sus contratos están en 6_contracts.md).
- Registro público de usuarios (los crea el admin por el CRUD de usuario).
- Refresh de token JWT (si expira, se vuelve a hacer login).
- Tests automatizados, i18n, notificaciones en tiempo real, despliegue a producción.

## 3. Requisitos funcionales

### RF1 — CRUD genérico por página
Cada tabla tiene su página `{Tabla}.razor` en `/{tabla}` con: tabla HTML de
registros, formulario crear/editar (compartido, prellenado al editar), eliminar
con confirmación, selects para campos FK (cargados desde la API) y mensajes de
éxito/error tras cada operación.

### RF2 — Login con JWT
`/login` pide email y contraseña; la verificación es **BCrypt del lado de la
API** (`POST autenticacion/token`); si es válida, el front guarda el token y lo
envía como `Authorization: Bearer` en **todas** las peticiones siguientes.

### RF3 — Control de acceso por roles y rutas
Tras el login se cargan los roles del usuario y las rutas permitidas de sus
roles (idealmente con **una sola consulta SQL** vía el endpoint de consultas de
la API; si no está disponible, con GETs por tabla como plan B). En **cada
navegación** se verifica `TieneAcceso(ruta)`: sin permiso → `/sin-acceso` (403);
sin sesión → `/login`. Usuario sin roles → rechazado con mensaje claro.

### RF4 — Sesión que sobrevive a F5
La sesión (usuario, token, roles, rutas) se guarda **encriptada** en
`ProtectedSessionStorage`: refrescar la página la restaura; cerrar la pestaña
la pierde. Manipular el valor almacenado la invalida.

### RF5 — Gestión de contraseñas
- `/cambiar-contrasena`: valida la nueva (6+ caracteres, mayúscula, número) y
  la guarda con `?camposEncriptar=contrasena` (hash BCrypt).
- `/recuperar-contrasena`: genera una temporal, la envía por SMTP y marca el
  usuario para **cambio forzado** en el siguiente login.

### RF6 — Factura maestro-detalle
`/factura` lista facturas y permite crear una nueva: cabecera con selects de
cliente y vendedor + tabla dinámica de renglones (producto, cantidad) con
agregar/quitar filas; los totales los calcula la BD (trigger) — el front solo
envía los renglones.

### RF7 — Descubrimiento dinámico de estructura
Al iniciar sesión, el front consulta la estructura de la BD a la API y cachea
PKs y FKs — las operaciones de actualizar/eliminar arman sus URLs con la PK
descubierta, no con nombres fijos.

## 4. Requisitos no funcionales

- **RNF1 — Blazor Server interactivo global:** `@rendermode InteractiveServer`
  en `App.razor` (eventos, SignalR y sesión disponibles en todas las páginas).
- **RNF2 — Resiliencia:** si la API no responde, mensajes de error en pantalla
  (nunca crash); los servicios capturan las excepciones HTTP.
- **RNF3 — Configuración externa:** `ApiBaseUrl` y `Smtp:*` en
  `appsettings.json`, sobrescribibles por variables de entorno
  (`ApiBaseUrl`, `Smtp__User`, `Smtp__Pass`) — la vía natural en contenedores.
- **RNF4 — Contenedor Docker:** puerto **8004**, imagen `dotnet/sdk:10.0` con
  `dotnet watch` (guardar un `.razor` recompila y reinicia solo).
- **RNF5 — Un circuito por usuario:** servicios registrados `AddScoped` — cada
  usuario tiene su propia instancia (su token no se comparte).

## 5. Criterios de aceptación

1. El front arranca (Docker o `dotnet run`) y sin sesión redirige a `/login`.
2. Login con un usuario válido de la tabla `usuario` (p. ej. `admin@correo.com`
   / `admin123` en la BD de prueba) → entra al Home con su nombre en la barra;
   con contraseña mala → alerta roja sin crash.
3. `/producto` lista los registros reales de la BD a través de la API **con
   token** (verificable en F12 → Network: header `Authorization: Bearer`).
4. Ciclo CRUD completo sobre `producto` (crear → editar → eliminar) con mensaje
   de éxito en cada paso y datos verificables en la BD.
5. Un usuario cuyo rol NO permite `/factura` es redirigido a `/sin-acceso` al
   intentar navegar allí (por clic o escribiendo la URL).
6. F5 conserva la sesión; cerrar la pestaña y volver a abrir exige login.
7. Cambiar contraseña rechaza claves débiles y acepta una válida; el nuevo hash
   BCrypt queda en la BD y el login siguiente funciona con la nueva.
8. Crear una factura con 2 renglones: la BD calcula subtotales y total (el
   front no los envía) y descuenta stock.

## 6. Glosario

| Término | Significado |
|---|---|
| Blazor Server | Modelo donde el C# corre en el servidor y el navegador se sincroniza por SignalR |
| Circuito | La conexión SignalR viva de UN usuario (estado por usuario) |
| `ProtectedSessionStorage` | sessionStorage del navegador, encriptado por el servidor (Data Protection) |
| JWT | Token firmado que el front presenta a la API como `Authorization: Bearer …` |
| Maestro-detalle | Formulario con cabecera (factura) + N renglones hijos (productosporfactura) |
| Descubrimiento dinámico | Preguntar a la API por PKs/FKs en runtime en vez de hardcodearlas |
