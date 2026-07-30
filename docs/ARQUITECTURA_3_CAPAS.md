# Arquitectura de 3 capas — Proyecto Paradigmas

Este documento sigue **el viaje completo de una petición**: desde el clic en el navegador hasta la base de datos y de vuelta. Léalo con el código abierto al lado.

---

## Mapa general

```
┌────────────────────────────────────────────────────────────────┐
│  NAVEGADOR                                                     │
│  http://localhost:8000/productos                               │
└──────────────┬─────────────────────────────────────────────────┘
               │ HTTP (HTML)
┌──────────────▼─────────────────────────────────────────────────┐
│  CAPA 1 — FRONT (Flask, carpeta front_flask/, puerto 8000)     │
│                                                                │
│  rutas/productos.py      → recibe la petición                  │
│  servicios/cliente_api.py→ llama a la API elegida              │
│  templates/*.html        → arma el HTML con los datos          │
│                                                                │
│  El front NUNCA toca la base de datos.                         │
└──────────────┬─────────────────────────────────────────────────┘
               │ HTTP (JSON)
┌──────────────▼─────────────────────────────────────────────────┐
│  CAPA 2 — API (FastAPI). Hay DOS para comparar:                │
│                                                                │
│  api_generica/ (8001)          api_facturas/ (8002)            │
│  Un solo CRUD que sirve        Un controller + servicio +      │
│  para CUALQUIER tabla:         repositorio POR ENTIDAD, con    │
│  /api/{tabla}                  validación Pydantic:            │
│                                /api/persona, /api/factura …    │
│                                                                │
│  Por dentro, ambas tienen 3 subcapas:                          │
│  controllers/ → reciben HTTP, retornan JSON                    │
│  servicios/   → lógica de negocio                              │
│  repositorios/→ SQL contra el motor elegido                    │
└──────────────┬─────────────────────────────────────────────────┘
               │ SQL (driver async)
┌──────────────▼─────────────────────────────────────────────────┐
│  CAPA 3 — BASE DE DATOS (elegida con DB_PROVIDER)              │
│                                                                │
│  PostgreSQL (asyncpg) | MariaDB (aiomysql) | SQL Server (odbc) │
│  Las tres tienen la MISMA base de datos: bdfacturas            │
│  (con triggers y procedimientos que protegen el negocio)       │
└────────────────────────────────────────────────────────────────┘
```

---

## El viaje de una petición: "listar productos"

**1. El navegador** pide `GET http://localhost:8000/productos/`.

**2. Flask** ([front_flask/rutas/productos.py](../front_flask/rutas/productos.py)) atiende la ruta:

```python
@bp_productos.route("/")
def listar():
    exito, resultado = _api().listar(TABLA)      # ← pide los datos a la API
    return render_template("productos_lista.html", productos=resultado)
```

**3. El cliente HTTP** ([front_flask/servicios/cliente_api.py](../front_flask/servicios/cliente_api.py)) traduce eso a una petición HTTP según la API activa:

- API genérica: `GET http://api-generica:8001/api/producto`
- API facturas: `GET http://api-facturas:8002/api/producto/`

**4. El controller de la API** recibe la petición y **delega** al servicio (no sabe nada de SQL):

```python
@router.get("/{tabla}")
async def listar(tabla: str, ...):
    servicio = crear_servicio_crud()
    filas = await servicio.listar(tabla, esquema, limite)
    return {"tabla": tabla, "total": len(filas), "datos": filas}
```

**5. El servicio** aplica las reglas de negocio (validar nombre de tabla, límites) y llama al repositorio.

**6. La fábrica de repositorios** mira `DB_PROVIDER` y entrega el repositorio del motor correcto (patrón **Factory**). Cada repositorio implementa la misma interfaz (patrón **Repository**), por eso el resto del código no cambia al cambiar de motor.

**7. El repositorio** ejecuta el SQL **parametrizado** con el driver async del motor y retorna filas como diccionarios.

**8. De vuelta**: repositorio → servicio → controller (JSON) → cliente_api (lista de dicts) → ruta Flask → plantilla Jinja (HTML) → navegador.

---

## ¿Por qué separar en capas? (los conceptos)

| Concepto | Qué significa aquí |
|---|---|
| **Separación de responsabilidades** | El front pinta pantallas; la API decide reglas; la BD guarda datos. Cada uno se puede cambiar sin romper los otros. |
| **Bajo acoplamiento** | El front funciona igual con las dos APIs (cámbielo en el menú y compruébelo). La API funciona igual con los 3 motores (`DB_PROVIDER`). |
| **Patrón Repository** | Todo el SQL vive en `repositorios/`. Si mañana llega otro motor, se escribe un repositorio nuevo y nada más. |
| **Patrón Factory** | `fabrica_repositorios.py` decide en un solo lugar qué repositorio crear según la configuración. |
| **Validación en el borde** | La API facturas usa modelos **Pydantic**: un dato mal formado se rechaza ANTES de llegar a la BD. |
| **Consultas parametrizadas** | Los valores nunca se concatenan al SQL → imposible la inyección SQL. |
| **Lógica en la BD** | Los triggers calculan subtotales/total y validan stock: reglas que deben cumplirse sin importar qué aplicación escriba en la BD. |

---

## Genérica vs. Facturas: ¿cuál es "mejor"?

Ninguna — son **dos paradigmas** con ventajas y costos:

| | API Genérica | API Facturas |
|---|---|---|
| Código | Poco (un CRUD para todo) | Mucho (12 × controller+servicio+repositorio) |
| Validación | Mínima (lo que diga la BD) | Estricta (Pydantic por entidad) |
| Documentación Swagger | Genérica | Específica por entidad, con tipos |
| Agregar una tabla nueva | Gratis (ya funciona) | Hay que programarla |
| Control fino por entidad | Difícil | Natural |

**Ejercicio sugerido:** cree un producto con `stock = -5` en las dos APIs (desde Swagger) y observe quién lo rechaza y quién lo deja pasar. Después mire dónde está esa validación en el código de `api_facturas`.

---

## Cómo cambiar el motor de base de datos

Las dos APIs leen la variable `DB_PROVIDER` (ver `docker-compose.yml`):

```powershell
# Cambiar a MariaDB
$env:DB_PROVIDER = "mariadb"; docker compose up -d

# Cambiar a SQL Server
$env:DB_PROVIDER = "sqlserver"; docker compose up -d

# Volver a PostgreSQL (el valor por defecto)
$env:DB_PROVIDER = "postgres"; docker compose up -d
```

Luego recargue el front: los datos ahora salen del otro motor. **Nada más cambió** — esa es la gracia de la arquitectura.

---

## Dónde está cada cosa

| Quiero ver… | Archivo |
|---|---|
| Cómo el front pide datos | [front_flask/servicios/cliente_api.py](../front_flask/servicios/cliente_api.py) |
| Un CRUD completo en el front | [front_flask/rutas/productos.py](../front_flask/rutas/productos.py) |
| El CRUD genérico (una tabla cualquiera) | [api_generica/controllers/entidades_controller.py](../api_generica/controllers/entidades_controller.py) |
| Un CRUD por entidad con validación | [api_facturas/controllers/persona_controller.py](../api_facturas/controllers/persona_controller.py) |
| Los modelos de validación | [api_facturas/models/](../api_facturas/models/) |
| La fábrica que elige el motor | `*/servicios/fabrica_repositorios.py` |
| El SQL real de cada motor | `*/repositorios/` |
| Los triggers y procedimientos | [db/](../db/) |
