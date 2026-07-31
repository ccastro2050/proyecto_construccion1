# Quickstart — Front Blazor (Blazor Server)

> **Documento 7 de 8** del spec kit. Validación rápida del front ya construido.
> Si aún no hay nada construido, empiece por [8_tasks.md](8_tasks.md).

---

## 1. Prerrequisito: la API y su base de datos

Se necesita una API corriendo en `http://localhost:8003` que cumpla los
contratos de [6_contracts.md](6_contracts.md) §2, conectada a la BD
`bdfacturas` (scripts incluidos en `script_bd/`; receta de montaje en
[5_data_model.md](5_data_model.md) §3).

## 2. Arrancar el front

```powershell
# Opción local (requiere .NET 10 SDK):
dotnet run          # appsettings.json ya apunta a http://localhost:8003
# abre en el puerto de launchSettings; con Docker queda fijo en 8004

# Opción Docker (el Dockerfile del proyecto; puerto 8004 con dotnet watch):
docker build -t front-blazor .
docker run -d -p 8004:8004 `
  -e ApiBaseUrl="http://host.docker.internal:8003" `
  front-blazor
```

## 3. Recorrido de validación (5 minutos, en el navegador)

1. **http://localhost:8004** → sin sesión, redirige solo a `/login`
   (spinner breve mientras intenta restaurar sesión: es el diseño).
2. **Login fallido**: `admin@correo.com` / `mala` → alerta roja
   "Contraseña incorrecta", sin crash.
3. **Login válido**: `admin@correo.com` / `admin123` → Home con el email en la
   barra superior y el sidebar con todas las tablas.
4. **F12 → Network** → abrir `/producto` → la petición a la API lleva el header
   `Authorization: Bearer eyJ…` (el JWT en acción) y la tabla muestra los 8
   productos de la BD.
5. **Ciclo CRUD**: crear `PR009 / Webcam / 5 / 120000` → mensaje verde y
   aparece en la tabla → editar el stock a 7 → eliminar con confirmación.
6. **Control de acceso**: entrar con un usuario de rol limitado (p. ej. un
   vendedor) → el sidebar/rutas se reducen; escribir a mano una URL prohibida
   → redirige a `/sin-acceso` (403).
7. **Sesión**: F5 conserva la sesión; cerrar la pestaña, abrir de nuevo →
   vuelve a pedir login.
8. **Factura maestro-detalle**: nueva factura con cliente, vendedor y 2
   renglones → los subtotales y el total los devuelve la BD (trigger), y el
   stock de los productos baja.
9. **Cambiar contraseña**: una débil (`abc`) → rechazada con el motivo; una
   válida (`Nueva123`) → aceptada; logout y login con la nueva.

## 4. Si algo falla

| Síntoma | Causa probable |
|---|---|
| `/login` con error "Error de conexión" | La API no está corriendo o `ApiBaseUrl` apunta mal |
| Login correcto pero "No tiene roles asignados" | El usuario no tiene filas en `rol_usuario` — es el contrato, no un bug |
| Todas las páginas de datos vacías con sesión activa | El JWT expiró (60 min): logout + login |
| Los botones no reaccionan | La página quedó sin `@rendermode InteractiveServer` (debe estar global en `App.razor`) o se cayó la conexión SignalR (revisar consola del navegador) |
| Excepción al leer la sesión al arrancar | Se intentó `ProtectedSessionStorage` en `OnInitializedAsync` — debe ser `OnAfterRenderAsync` |
| "Recuperar contraseña" no envía correo | Faltan `Smtp__User`/`Smtp__Pass` en el entorno (el repo no trae credenciales, a propósito) |
| En Docker, cambié un `.razor` y no pasa nada | `dotnet watch` tarda unos segundos: revisar `docker logs` del contenedor |
| La sesión "se pierde" al reiniciar el contenedor | Data Protection genera claves nuevas al recrear el contenedor: los valores encriptados viejos se invalidan — volver a hacer login |
