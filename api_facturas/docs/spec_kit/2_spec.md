# Especificación — API Facturas (CRUD por entidad)

> **Documento 2 de 8** de un spec kit **autocontenido**: con esta carpeta se
> reconstruye la API completa desde cero, como proyecto independiente.
>
> | # | Documento | Contenido |
> |---|---|---|
> | 1 | [1_constitution.md](1_constitution.md) | Principios innegociables |
> | 2 | **2_spec.md** (este) | QUÉ construir: requisitos y criterios de aceptación |
> | 3 | [3_plan.md](3_plan.md) | CÓMO: stack, estructura, diseño de cada capa |
> | 4 | [4_research.md](4_research.md) | Decisiones técnicas y alternativas *(lectura opcional)* |
> | 5 | [5_data_model.md](5_data_model.md) | Las 12 tablas, la lógica en BD y los modelos Pydantic |
> | 6 | [6_contracts.md](6_contracts.md) | TODOS los endpoints HTTP con formatos exactos |
> | 7 | [7_quickstart.md](7_quickstart.md) | Arranque y smoke test de validación |
> | 8 | [8_tasks.md](8_tasks.md) | Orden de construcción por fases verificables |

---

## 1. Propósito

Construir una API REST en **FastAPI** para la base de datos de facturación
`bdfacturas`, con **un CRUD por cada una de sus 12 entidades**, validación de
tipos con **modelos Pydantic**, arquitectura estricta en capas
(controller → servicio → repositorio, con interfaces y fábrica) y soporte para
**PostgreSQL, MySQL/MariaDB y SQL Server** eligiendo el motor con una variable
de entorno (`DB_PROVIDER`), sin cambiar código.

Es un proyecto **didáctico**: enseña el costo y el beneficio de la validación
tipada por entidad, los principios SOLID (interfaces, inversión de dependencias,
fábrica) y la independencia del motor de base de datos. Todo el código se escribe
en español con comentarios que explican cada decisión.

## 2. Contexto e independencia

- La API es autónoma: corre sola con `uvicorn main:app --port 8012` o en Docker.
  Su única dependencia externa es una BD `bdfacturas`
  ([5_data_model.md](5_data_model.md) §6 explica cómo montarla suelta).
- Cualquier cliente HTTP la consume (Swagger, un frontend, otro servicio);
  ninguno es requisito para construirla o probarla.
- La lógica de facturación (subtotales, totales, stock) **vive en la base de
  datos** (trigger + procedimientos): la API no la reimplementa.

## 3. Alcance

**Incluye:**
- CRUD tipado de las 12 entidades (endpoints exactos en [6_contracts.md](6_contracts.md)).
- Verificación de contraseña de usuario contra hash BCrypt.
- Encriptación automática de `usuario.contrasena` al crear/actualizar.
- Un controller genérico de respaldo (`/api/{tabla}`) para tablas sin controller propio.
- Selección de motor por configuración; los 3 motores se comportan idéntico.
- Documentación interactiva en `/docs` (Swagger UI) y `/redoc`.

**No incluye:**
- Autenticación/autorización de la API (JWT, sesiones, API keys).
- Paginación real, búsqueda ni ordenamiento (solo `limite`, tope 1000).
- Creación transaccional de factura con detalle (la hacen los SP de la BD).
- Migraciones de esquema.

## 4. Requisitos funcionales

### RF1 — Patrón CRUD estándar por entidad
Para persona, empresa, cliente, vendedor, producto, factura, rol, usuario y ruta
(prefix `/api/<entidad>`, PK según [5_data_model.md](5_data_model.md)):

```
GET    /api/<entidad>/          → 200 {tabla,total,datos} | 204 si vacío
GET    /api/<entidad>/{pk}      → 200 | 404
POST   /api/<entidad>/          body validado por el modelo Pydantic → 200 | 422 | 500
PUT    /api/<entidad>/{pk}      body Pydantic; la PK se excluye del SET → 200 | 404
DELETE /api/<entidad>/{pk}      → 200 | 404
```

Query param `esquema` en todos; `limite` en los listados. Formatos exactos de
respuesta y errores: [6_contracts.md](6_contracts.md) §0–§1.

### RF2 — Excepciones al patrón
- **usuario**: endpoint extra `POST /api/usuario/verificar-contrasena`
  (200 válida / 401 incorrecta / 404 no existe); crear y actualizar re-encriptan
  la contraseña con BCrypt costo 12.
- **ruta**: su clave contiene barras (`/home`) → parámetros con convertidor
  `{valor_ruta:path}` en GET/PUT/DELETE.
- **productosporfactura**, **rol_usuario** (prefix `/api/rol-usuario`, con guion)
  y **rutarol**: tablas puente **sin PUT**, con búsquedas secundarias
  (`/factura/{n}`, `/usuario/{email}`, `/rol/{id|nombre}`) y DELETE por los dos
  segmentos de la PK compuesta.

> ⚠️ **Decisión a tomar al reconstruir:** en el código original los DELETE de PK
> compuesta solo filtran por el primer segmento (borran de más). Elegir: réplica
> fiel o corrección (filtrar por ambas columnas), y documentarlo.

### RF3 — Controller genérico de respaldo
Un `entidades_controller` con CRUD sobre `/api/{tabla}` (cualquier tabla, body
`dict` sin validación, con `campos_encriptar` opcional y `verificar-contrasena`
genérico), **registrado de último** para que las rutas específicas tengan
prioridad. Endpoints en [6_contracts.md](6_contracts.md) §3.

> ⚠️ En el código original este controller está roto (su servicio llama métodos
> públicos que las clases base solo exponen con `_`). La reconstrucción debe
> exponer las 6 operaciones como públicas en las bases.

### RF4 — Selección de motor por configuración
`DB_PROVIDER` ∈ {`postgres`/`postgresql`, `mariadb`/`mysql`, `sqlserver`/
`sqlserverexpress`/`localdb`} + cadenas `DB_POSTGRES`, `DB_MARIADB`, `DB_MYSQL`,
`DB_SQLSERVER`. Cambiar de motor no toca código. Los tipos de columnas se
detectan consultando `information_schema` para convertir los valores que llegan
como texto por la URL.

### RF5 — Diagnóstico
`GET /` → `{"mensaje": "API Facturas CRUD activa.", "docs": "/docs", "redoc": "/redoc"}`
(usable como healthcheck por cualquier consumidor).

## 5. Requisitos no funcionales

- **RNF1 — Async de extremo a extremo:** FastAPI + SQLAlchemy 2 async + drivers
  async (asyncpg, aiomysql, aioodbc).
- **RNF2 — Arquitectura en capas con contratos:** controller → servicio →
  repositorio; interfaces `typing.Protocol`; fábrica que elige el repositorio por
  proveedor; inyección de dependencias por constructor.
- **RNF3 — El orden de registro de routers importa:** los 12 específicos primero,
  el genérico al final.
- **RNF4 — Docker:** imagen `python:3.12-slim` + driver ODBC msodbcsql18,
  puerto **8012**.
- **RNF5 — Seguridad básica:** valores SQL siempre parametrizados; contraseñas
  jamás en texto plano (BCrypt).
- **RNF6 — CORS (mejora recomendada):** el original no lo trae (el front lo
  consume del lado servidor); agregar `CORSMiddleware` abierto si algún cliente
  de navegador la llamará directo.
- **RNF7 — Español didáctico:** docstrings de módulo, comentarios de bloque
  `# ====`, mensajes de error en español.

## 6. Criterios de aceptación

Con la BD de ejemplo cargada ([5_data_model.md](5_data_model.md) §4):

1. `GET http://localhost:8012/` responde el diagnóstico y `/docs` abre Swagger UI
   con los 13 tags.
2. `GET /api/persona/` lista 6 personas; `GET /api/persona/P001` → Ana Torres;
   `GET /api/persona/NOEXISTE` → 404 estructurado.
3. `POST /api/persona/` sin `nombre` → **422 de Pydantic** (la validación tipada
   es la razón de ser de esta API).
4. Ciclo completo crear→consultar→editar→eliminar sobre `producto` (PR009) desde
   Swagger UI, con las respuestas de [6_contracts.md](6_contracts.md) §0.
5. `POST /api/usuario/` guarda `contrasena` como hash `$2b$12$…` de 60 caracteres;
   `verificar-contrasena` → 200/401/404 según el caso.
6. `GET /api/productosporfactura/factura/1` devuelve solo los renglones de la
   factura 1; `POST` de un renglón nuevo dispara el trigger (stock y total cambian
   en la BD); stock insuficiente → 500 con el mensaje del trigger.
7. `GET /api/ruta//home` funciona (convertidor `:path`).
8. Eliminar una persona referenciada por cliente → 500 con el error de FK en `detalle`.
9. Una tabla creada a mano en la BD (sin controller propio) responde por
   `/api/{tabla}` vía el controller genérico.
10. Los puntos 2–7 se repiten idénticos con `DB_PROVIDER=mariadb` y `sqlserver`.
