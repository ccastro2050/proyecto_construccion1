# Tareas — API Genérica CRUD

> **Documento 8 de 8** del spec kit: el orden de construcción. Cada fase termina
> en algo **verificable**. Requisitos: [2_spec.md](2_spec.md) · técnica:
> [3_plan.md](3_plan.md) · endpoints: [6_contracts.md](6_contracts.md) ·
> validación final: [7_quickstart.md](7_quickstart.md).

---

## Fase 0 — Base de datos de prueba y esqueleto
- [ ] Montar la BD `bdfacturas` para probar contra ella
      ([5_data_model.md](5_data_model.md) §2).
- [ ] Crear carpeta `api_generica/` con subcarpetas `controllers/`, `servicios/`
      (`abstracciones/`, `conexion/`, `utilidades/`), `repositorios/` (`abstracciones/`)
      y sus `__init__.py`.
- [ ] Escribir `requirements.txt` con las dependencias del plan (§1).
- [ ] Crear entorno virtual e instalar: `pip install -r requirements.txt`.

**Verificar:** `python -c "import fastapi, sqlalchemy, bcrypt"` no falla.

## Fase 1 — Configuración
- [ ] `config.py`: `DatabaseSettings` (prefijo `DB_`, campos `provider`, `postgres`,
      `mysql`, `mariadb`, `sqlserver`, `sqlserverexpress`, `localdb`),
      `Settings` (debug, environment, database) y `get_settings()` con `@lru_cache`.
- [ ] Soportar `.env` + `.env.development` según `ENVIRONMENT`.

**Verificar:** con un `.env` de prueba, `get_settings().database.provider` devuelve lo esperado.

## Fase 2 — Contratos y utilidades
- [ ] `servicios/abstracciones/i_proveedor_conexion.py` (Protocol).
- [ ] `repositorios/abstracciones/i_repositorio_lectura_tabla.py` (Protocol, 6 métodos async).
- [ ] `servicios/abstracciones/i_servicio_crud.py` (Protocol).
- [ ] `servicios/utilidades/encriptacion_bcrypt.py`: `encriptar()` y `verificar()`.
- [ ] `servicios/conexion/proveedor_conexion.py`: `proveedor_actual` y
      `obtener_cadena_conexion()` con mensajes de error claros.

**Verificar:** `verificar("abc", encriptar("abc"))` es `True`; con proveedor inválido,
`obtener_cadena_conexion()` lanza `ValueError` listando las opciones.

## Fase 3 — Primer repositorio: PostgreSQL
- [ ] `repositorios/repositorio_lectura_postgresql.py`: engine lazy, helpers de
      tipos (`_detectar_tipo_columna`, `_convertir_valor`, `_serializar_valor`)
      y los 6 métodos CRUD con identificadores `"entre comillas"` y esquema `public`.

**Verificar:** con la BD de la Fase 0 levantada, un script suelto que instancie el
repositorio lista `producto` y filtra `factura` por `numero=1`.

## Fase 4 — Servicio y fábrica
- [ ] `servicios/servicio_crud.py`: validaciones de entrada, normalización de
      esquema/límite, y `verificar_contrasena()` que devuelve `(código, mensaje)`.
- [ ] `servicios/fabrica_repositorios.py`: diccionario proveedor→clase,
      `crear_repositorio_lectura()` y `crear_servicio_crud()`.

**Verificar:** `crear_servicio_crud()` devuelve un servicio funcional con
`DB_PROVIDER=postgres`; con un proveedor desconocido lanza `ValueError`.

## Fase 5 — Controller y aplicación
- [ ] `controllers/entidades_controller.py`: los 6 endpoints (RF1–RF6) con la
      traducción de excepciones del plan (§4.6) y respuestas envueltas.
- [ ] `main.py`: app FastAPI (título, versión, `docs_url="/swagger"`), CORS abierto,
      `include_router`, endpoint `/` de diagnóstico.

**Verificar:** `uvicorn main:app --port 8001` y en `http://localhost:8001/swagger`
probar: listar producto (200), tabla vacía (204), factura/numero/1 (200),
crear/actualizar/eliminar persona (200/200/200 y 404 con clave inexistente).

## Fase 6 — Los otros dos motores
- [ ] `repositorio_lectura_mysql_mariadb.py`: backticks, sin esquema antepuesto,
      mismos 6 métodos.
- [ ] `repositorio_lectura_sqlserver.py`: corchetes `[...]`, `TOP (n)`, esquema `dbo`.
- [ ] Registrar ambos en la fábrica (ya previsto en el diccionario).

**Verificar:** repetir las pruebas de la Fase 5 con `DB_PROVIDER=mariadb` y
`DB_PROVIDER=sqlserver` — mismo comportamiento, sin cambiar código.

## Fase 7 — BCrypt de extremo a extremo
- [ ] Probar `POST /api/usuario?campos_encriptar=contrasena` → el valor guardado
      es un hash de 60 caracteres que empieza por `$2b$12$`.
- [ ] Probar `POST /api/usuario/verificar-contrasena` → 200 / 401 / 404 según el caso.

## Fase 8 — Docker y cierre
- [ ] `Dockerfile` según el plan (§5), con msodbcsql18 — build y run standalone.
- [ ] `.gitignore` (`__pycache__/`, `.env*`, `.venv/`).
- [ ] Opcional — orquestar con docker-compose: servicio en el puerto 8001 con
      el código montado como volumen + `--reload`, y las variables `DB_*`
      inyectadas por `environment:` (hosts internos de la red de compose en
      lugar de `localhost`).

**Verificar:** [7_quickstart.md](7_quickstart.md) completo con los 3 motores —
equivale a los criterios de aceptación de [2_spec.md](2_spec.md) §5, incluido el
cambio de motor.
