# Quickstart — API Facturas

> **Documento 7 de 8** del spec kit. Validación rápida de la API ya construida
> (o del avance por fases de [8_tasks.md](8_tasks.md)). Si aún no hay nada
> construido, empiece por [8_tasks.md](8_tasks.md).

---

## 1. Prerrequisito: la base de datos

Montar `bdfacturas` con los scripts incluidos en `database/` — un `docker run`
por motor, receta exacta en [5_data_model.md](5_data_model.md) §6. La mínima,
solo PostgreSQL:

```powershell
docker run -d --name bdfacturas -p 15448:5432 `
  -e POSTGRES_DB=bdfacturas_postgres_local `
  -e POSTGRES_USER=paradigmas -e POSTGRES_PASSWORD=paradigmas123 `
  -v ${PWD}/database/bdfacturas_postgres.sql:/docker-entrypoint-initdb.d/init.sql:ro `
  postgres:16-alpine
```

## 2. Arrancar la API

```powershell
# local (desde la carpeta api_facturas, con el venv activo)
$env:DB_PROVIDER = "postgres"
$env:DB_POSTGRES = "postgresql+asyncpg://paradigmas:paradigmas123@localhost:15448/bdfacturas_postgres_local"
uvicorn main:app --port 8012 --reload
```

(En Docker: `docker build -t api-facturas . ; docker run -p 8012:8012 -e DB_PROVIDER=... -e DB_POSTGRES=... api-facturas` —
con la BD en otro contenedor, usar `host.docker.internal` en la cadena.)

## 3. Smoke test (5 minutos)

```powershell
# 1. Diagnóstico
curl http://localhost:8012/
# → {"mensaje":"API Facturas CRUD activa.","docs":"/docs","redoc":"/redoc"}

# 2. Lecturas
curl http://localhost:8012/api/persona/          # 6 personas
curl http://localhost:8012/api/persona/P001      # Ana Torres
curl -i http://localhost:8012/api/persona/ZZZ    # 404 estructurado

# 3. Validación Pydantic (la razón de ser de esta API)
curl -i -X POST http://localhost:8012/api/persona/ -H "Content-Type: application/json" -d '{\"codigo\":\"P999\"}'
# → 422 (falta "nombre")

# 4. Ciclo CRUD completo
curl -X POST http://localhost:8012/api/producto/ -H "Content-Type: application/json" `
     -d '{\"codigo\":\"PR009\",\"nombre\":\"Webcam\",\"stock\":5,\"valorunitario\":120000}'
curl -X PUT  http://localhost:8012/api/producto/PR009 -H "Content-Type: application/json" `
     -d '{\"codigo\":\"PR009\",\"nombre\":\"Webcam HD\",\"stock\":7,\"valorunitario\":120000}'
curl -X DELETE http://localhost:8012/api/producto/PR009

# 5. BCrypt
curl -X POST http://localhost:8012/api/usuario/ -H "Content-Type: application/json" `
     -d '{\"email\":\"qa@test.com\",\"contrasena\":\"secreto1\"}'
curl -X POST "http://localhost:8012/api/usuario/verificar-contrasena?valor_usuario=qa@test.com&valor_contrasena=secreto1"   # 200
curl -i -X POST "http://localhost:8012/api/usuario/verificar-contrasena?valor_usuario=qa@test.com&valor_contrasena=mala"   # 401
curl -X DELETE http://localhost:8012/api/usuario/qa@test.com

# 6. El trigger de la BD trabaja
curl http://localhost:8012/api/producto/PR003                     # anotar stock
curl -X POST http://localhost:8012/api/productosporfactura/ -H "Content-Type: application/json" `
     -d '{\"fknumfactura\":1,\"fkcodproducto\":\"PR003\",\"cantidad\":1,\"subtotal\":0}'
curl http://localhost:8012/api/producto/PR003                     # stock bajó 1
curl http://localhost:8012/api/factura/1                          # total subió
curl -X DELETE http://localhost:8012/api/productosporfactura/1/PR003
```

O todo lo anterior con clics en **http://localhost:8012/docs**.

## 4. Cambio de motor (la prueba de fuego)

```powershell
$env:DB_PROVIDER = "mariadb"
$env:DB_MARIADB  = "mysql+aiomysql://paradigmas:paradigmas123@localhost:13316/bdfacturas_mariadb_local"
# reiniciar uvicorn (get_settings está cacheado) y repetir el paso 3: idéntico
```

## 5. Si algo falla

| Síntoma | Causa probable |
|---|---|
| `Verificar DB_POSTGRES en .env` | Falta la variable de cadena del proveedor activo |
| 500 con "Error PostgreSQL al consultar" | La BD no está arriba o la cadena apunta mal |
| 422 inesperado | El body no cumple el modelo — ver 5_data_model.md §5 |
| 500 con mensaje de stock | Es el trigger validando — comportamiento correcto |
| `/api/{tabla}` genérico da 500 | Las bases no exponen las operaciones públicas (research D11.1) |
