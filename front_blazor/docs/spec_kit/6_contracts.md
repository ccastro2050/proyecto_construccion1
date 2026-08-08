# Contratos — Front Blazor (Blazor Server)

> **Documento 6 de 8** del spec kit. Dos contratos: (1) las **rutas que el
> front expone** al usuario y (2) los **endpoints de la API que consume** —
> cualquier API que cumpla §2 sirve. Más (3) el comportamiento del guardián y
> (4) la configuración externa.

---

## 1. Rutas que el front expone (páginas)

| Ruta | Página | Acceso | Qué hace |
|---|---|---|---|
| `/` | Home | sesión | Bienvenida + estado |
| `/login` | Login | pública | Email + contraseña → sesión (EmptyLayout, sin sidebar) |
| `/producto` `/persona` `/usuario` `/empresa` `/rol` `/ruta` `/cliente` `/vendedor` | CRUD | sesión + permiso de rol | Tabla + formulario crear/editar + eliminar con confirmación |
| `/factura` | Factura | sesión + permiso | Lista + creación maestro-detalle |
| `/cambiar-contrasena` | CambiarContrasena | sesión | Valida (6+, mayúscula, número) y guarda con BCrypt |
| `/recuperar-contrasena` | RecuperarContrasena | pública | Temporal por SMTP + cambio forzado |
| `/sin-acceso` | SinAcceso | sesión | Página 403 |

## 2. Endpoints de la API que consume (el contrato que otra API debe cumplir)

Base: `ApiBaseUrl` (config). Todas las llamadas de datos llevan
`Authorization: Bearer {token}` cuando hay sesión.

### 2.1 CRUD genérico (lo usa `ApiService` para cada tabla)

```
GET    /api/{tabla}?limite=N       → 200 { tabla, esquema, total, datos:[{col:val,…}] } · 204 vacía
POST   /api/{tabla}                → 200 { estado, mensaje }         body: {col:val,…}
PUT    /api/{tabla}/{pk}/{valor}   → 200 { estado, mensaje, filasAfectadas } · 404
DELETE /api/{tabla}/{pk}/{valor}   → 200 { estado, mensaje, filasEliminadas } · 404
       …/{pk}/{valor}?camposEncriptar=contrasena   ← guarda esa columna como hash BCrypt
```

### 2.2 Autenticación y seguridad (lo usa `AuthService`)

```
POST /api/Autenticacion/token
     body { tabla:"usuario", campoUsuario:"email", campoContrasena:"contrasena",
            usuario, contrasena }
     → 200 { token, expiracion } · 401 contraseña incorrecta · 404 usuario no existe

GET  /api/estructuras/basedatos    → estructura de la BD (PKs y FKs por tabla)

POST /api/consultas/ejecutarconsultaparametrizada
     body { consulta: "SELECT … JOIN … WHERE u.email = @email", parametros:{email} }
     → 200 { resultados:[…], total }        ← roles y rutas del usuario en 1 SQL
     (si la API no lo ofrece, el front usa el plan B: GETs por tabla de §2.1)
```

### 2.3 Procedimientos almacenados (lo usa `SpService`, facturación)

```
POST /api/procedimientos/ejecutarsp    body { nombreSP, …parámetros }
     → 200 { procedimiento, resultados, total, mensaje }
```

## 3. Contrato del guardián (MainLayout)

| Situación | Comportamiento |
|---|---|
| Primera carga sin sesión | spinner → `Restaurar()` no encuentra nada → redirect `/login` |
| Login correcto | token + roles + rutas en sesión encriptada → redirect `/` (o `/cambiar-contrasena` si está forzado) |
| Usuario sin roles | login rechazado con mensaje "no tiene roles asignados" |
| Navegación a ruta sin permiso (clic o URL) | `LocationChanged` → `TieneAcceso()` = false → redirect `/sin-acceso` |
| F5 | sesión restaurada desde `ProtectedSessionStorage` (encriptada) |
| Cerrar pestaña | sesión perdida → próxima visita exige login |
| API caída | mensajes de error en pantalla; la app no crashea |

## 4. Configuración externa (variables de entorno sobre appsettings.json)

| Variable | Default (sin Docker) | Ejemplo en docker-compose (hosts internos) |
|---|---|---|
| `ApiBaseUrl` | `http://localhost:8013` | `http://api-generica-csharp:8013` |
| `Smtp__Host` / `Smtp__Port` | `smtp.gmail.com` / `587` | ídem |
| `Smtp__User` / `Smtp__Pass` / `Smtp__From` | vacíos (recuperar contraseña deshabilitado) | inyectados desde el entorno del host |

**Regla:** el repositorio nunca contiene credenciales SMTP reales — se
inyectan por entorno o en `appsettings.Development.json` (ignorado por git).
