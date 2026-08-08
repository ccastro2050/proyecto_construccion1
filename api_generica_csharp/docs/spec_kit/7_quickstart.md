# Quickstart — API Genérica C# (ASP.NET Core)

> **Documento 7 de 8** del spec kit. Validación rápida de la API ya construida.
> Si aún no hay nada construido, empiece por [8_tasks.md](8_tasks.md).

---

## 1. Prerrequisito: una base de datos

Montar `bdfacturas` con el script incluido en `script_bd/` — un `docker run`
por motor, receta exacta en [5_data_model.md](5_data_model.md) §3
(PostgreSQL en `localhost:15442`, usuario `paradigmas`/`paradigmas123`).

## 2. Arrancar la API

```powershell
# Opción local (requiere .NET 10 SDK):
dotnet run          # appsettings.json ya apunta a localhost:15442 con DatabaseProvider=Postgres

# Opción Docker (el Dockerfile del proyecto; puerto 8013 con dotnet watch):
docker build -t api-generica-csharp .
docker run -d -p 8013:8013 `
  -e ConnectionStrings__Postgres="Host=host.docker.internal;Port=15442;Database=bdfacturas_postgres_local;Username=paradigmas;Password=paradigmas123;" `
  api-generica-csharp
```

## 3. Smoke test (5 minutos, en PowerShell)

```powershell
# 1. Bienvenida y documentación
curl http://localhost:8013/                    # bienvenida
# abrir http://localhost:8013/swagger (botón Authorize) y /redoc

# 2. El endpoint protegido SIN token → 401 (es el contrato, no un error)
curl -i http://localhost:8013/api/producto

# 3. Obtener token JWT (usuario semilla de bdfacturas)
$body = '{"tabla":"usuario","campoUsuario":"email","campoContrasena":"contrasena","usuario":"admin@correo.com","contrasena":"admin123"}'
$t = Invoke-RestMethod -Uri http://localhost:8013/api/Autenticacion/token -Method Post -ContentType "application/json" -Body $body
$h = @{ Authorization = "Bearer $($t.token)" }

# 4. Con token → 200 con envoltura {tabla, esquema, limite, total, datos}
Invoke-RestMethod -Uri http://localhost:8013/api/producto -Headers $h

# 5. Lecturas por clave (anónimas) — conversión texto→tipo automática
curl http://localhost:8013/api/factura/numero/1
curl -i http://localhost:8013/api/factura/numero/99          # 404

# 6. Ciclo CRUD sobre persona (anónimo)
curl -X POST http://localhost:8013/api/persona -H "Content-Type: application/json" `
     -d '{\"codigo\":\"P999\",\"nombre\":\"Test\",\"email\":\"t@t.co\",\"telefono\":\"300\"}'
curl -X PUT  http://localhost:8013/api/persona/codigo/P999 -H "Content-Type: application/json" `
     -d '{\"nombre\":\"Test Editado\"}'
curl http://localhost:8013/api/persona/codigo/P999
curl -X DELETE http://localhost:8013/api/persona/codigo/P999

# 7. BCrypt de extremo a extremo
curl -X POST "http://localhost:8013/api/usuario?camposEncriptar=contrasena" `
     -H "Content-Type: application/json" -d '{\"email\":\"qa@test.com\",\"contrasena\":\"secreto1\"}'
curl -X POST "http://localhost:8013/api/usuario/verificar-contrasena?campoUsuario=email&campoContrasena=contrasena&valorUsuario=qa@test.com&valorContrasena=secreto1"   # 200
curl -X DELETE http://localhost:8013/api/usuario/email/qa@test.com

# 8. Consulta SELECT parametrizada
curl -X POST http://localhost:8013/api/consultas/ejecutarconsultaparametrizada `
     -H "Content-Type: application/json" `
     -d '{\"consulta\":\"SELECT * FROM producto WHERE stock > @minimo\",\"parametros\":{\"minimo\":20}}'

# 9. Metadatos y diagnóstico
curl http://localhost:8013/api/estructuras/producto/modelo
curl http://localhost:8013/api/diagnostico/conexion          # ¿a qué BD estoy conectado realmente?
```

## 4. Cambio de motor (la prueba de fuego)

```powershell
# 1. Montar el motor alterno con su script de script_bd/ (5_data_model.md §3)
# 2. Cambiar "DatabaseProvider" a "mariadb" o "sqlserver" — por appsettings.json
#    o por variable de entorno:
$env:DatabaseProvider = "mariadb"
dotnet run
# 3. Repetir el paso 3 completo: comportamiento idéntico, sin cambiar código
```

## 5. Si algo falla

| Síntoma | Causa probable |
|---|---|
| 401 en `GET /api/{tabla}` | Es el contrato: falta el header `Authorization: Bearer` o el token expiró (60 min) — pedir otro |
| `No se encontró la cadena de conexión para el proveedor 'X'` | `DatabaseProvider` no coincide con ninguna clave de `ConnectionStrings` |
| 500 con detalle de conexión | BD abajo o cadena apuntando mal (dentro de Docker: hosts `postgres`/`mariadb`/`sqlserver`; fuera: `localhost:15442/13316/11443`) |
| 204 donde esperaba datos | La tabla existe pero está vacía (es el contrato) |
| El cambio de proveedor no surte efecto | El `switch` de Program.cs corre al arrancar: reiniciar el proceso/contenedor |
| En Docker, cambié un `.cs` y no pasa nada | `dotnet watch` tarda unos segundos en recompilar: revisar `docker logs` del contenedor |
| Cambié el `.csproj` y falla | Paquetes nuevos requieren `dotnet restore` (local) o reconstruir la imagen (`docker build`) |
| 403 en `/api/consultas` | La consulta no es SELECT o toca una tabla de `TablasProhibidas` |
