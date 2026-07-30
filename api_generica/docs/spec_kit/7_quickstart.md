# Quickstart — API Genérica CRUD

> **Documento 7 de 8** del spec kit. Validación rápida de la API ya construida.
> Si aún no hay nada construido, empiece por [8_tasks.md](8_tasks.md).

---

## 1. Prerrequisito: una base de datos

Opción A — proyecto padre: `docker compose up -d` en la raíz (3 motores con
`bdfacturas`). Opción B — PostgreSQL suelto: [5_data_model.md](5_data_model.md) §2.

## 2. Arrancar la API

```powershell
# local (desde api_generica, con el venv activo)
$env:DB_PROVIDER = "postgres"
$env:DB_POSTGRES = "postgresql+asyncpg://paradigmas:paradigmas123@localhost:15432/bdfacturas_postgres_local"
uvicorn main:app --port 8001 --reload
```

(En Docker: `docker build -t api-generica . ; docker run -p 8001:8001 -e DB_PROVIDER=... -e DB_POSTGRES=... api-generica`.)

## 3. Smoke test (5 minutos)

```powershell
# 1. Diagnóstico y documentación
curl http://localhost:8001/            # {"mensaje":"API CRUD genérica funcionando",...}
# abrir http://localhost:8001/swagger en el navegador

# 2. Lecturas genéricas — la MISMA ruta sirve para cualquier tabla
curl http://localhost:8001/api/producto
curl http://localhost:8001/api/persona
curl http://localhost:8001/api/factura/numero/1       # conversión texto→int automática
curl -i http://localhost:8001/api/factura/numero/99   # 404

# 3. Ciclo CRUD sobre persona
curl -X POST http://localhost:8001/api/persona -H "Content-Type: application/json" `
     -d '{\"codigo\":\"P999\",\"nombre\":\"Test\",\"email\":\"t@t.co\",\"telefono\":\"300\"}'
curl -X PUT  http://localhost:8001/api/persona/codigo/P999 -H "Content-Type: application/json" `
     -d '{\"nombre\":\"Test Editado\"}'
curl http://localhost:8001/api/persona/codigo/P999
curl -X DELETE http://localhost:8001/api/persona/codigo/P999

# 4. BCrypt de extremo a extremo
curl -X POST "http://localhost:8001/api/usuario?campos_encriptar=contrasena" `
     -H "Content-Type: application/json" -d '{\"email\":\"qa@test.com\",\"contrasena\":\"secreto1\"}'
curl -X POST "http://localhost:8001/api/usuario/verificar-contrasena?campo_usuario=email&campo_contrasena=contrasena&valor_usuario=qa@test.com&valor_contrasena=secreto1"   # 200
curl -i -X POST "http://localhost:8001/api/usuario/verificar-contrasena?campo_usuario=email&campo_contrasena=contrasena&valor_usuario=qa@test.com&valor_contrasena=mala"   # 401
curl -X DELETE http://localhost:8001/api/usuario/email/qa@test.com

# 5. Los errores de la BD llegan legibles
curl -i -X DELETE http://localhost:8001/api/persona/codigo/P001   # 500: FK (P001 es cliente)
```

## 4. Cambio de motor (la prueba de fuego)

```powershell
$env:DB_PROVIDER = "mariadb"
$env:DB_MARIADB  = "mysql+aiomysql://paradigmas:paradigmas123@localhost:13306/bdfacturas_mariadb_local"
# reiniciar uvicorn (settings cacheados) y repetir el paso 3: comportamiento idéntico
```

## 5. Si algo falla

| Síntoma | Causa probable |
|---|---|
| `No se encontró cadena de conexión para 'postgres'` | Falta `DB_POSTGRES` en el entorno/.env |
| 500 "Error PostgreSQL al consultar" | BD abajo o cadena mal apuntada |
| 204 donde esperaba datos | La tabla existe pero está vacía (es el contrato) |
| El cambio de `DB_PROVIDER` no surte efecto | `get_settings()` está cacheado: reiniciar el proceso |
| Import error de `aioodbc`/ODBC | Solo afecta SQL Server: instalar msodbcsql18 (en Docker ya viene) |
