# Tareas — API Facturas

> **Documento 8 de 8** del spec kit: el orden de construcción. Cada fase termina
> en algo **verificable**. Requisitos: [2_spec.md](2_spec.md) · técnica:
> [3_plan.md](3_plan.md) · datos: [5_data_model.md](5_data_model.md) ·
> endpoints: [6_contracts.md](6_contracts.md) · validación final: [7_quickstart.md](7_quickstart.md).
>
> Estrategia: construir UN corte vertical completo (persona) de punta a punta,
> verificarlo, y solo entonces replicar el patrón a las demás entidades.

---

## Fase 0 — Base de datos y esqueleto
- [ ] Montar la BD `bdfacturas` (script `database/bdfacturas_postgres.sql`;
      cómo correrla suelta: [5_data_model.md](5_data_model.md) §6).
- [ ] Crear el árbol de carpetas del plan (§2) con TODOS sus `__init__.py`.
- [ ] `requirements.txt` (plan §1) + entorno virtual + `pip install`.
- [ ] `.gitignore` (venv/, `__pycache__/`, *.pyc, .env).

**Verificar:** `python -c "import fastapi, sqlalchemy, bcrypt, asyncpg"` no falla;
un cliente SQL ve las 12 tablas con datos.

## Fase 1 — Configuración y utilidades transversales
- [ ] `config.py`: `DatabaseSettings` (prefijo `DB_`, 7 campos) + `Settings` +
      `get_settings()` con `@lru_cache` (plan §3).
- [ ] `servicios/abstracciones/i_proveedor_conexion.py` (Protocol) y
      `servicios/conexion/proveedor_conexion.py`.
- [ ] `servicios/utilidades/encriptacion_bcrypt.py`: `encriptar()` / `verificar()` (plan §4).

**Verificar:** con `DB_PROVIDER=postgres` y `DB_POSTGRES` seteados,
`ProveedorConexion().obtener_cadena_conexion()` devuelve la cadena; con un
proveedor inválido lanza `ValueError` listando opciones;
`verificar("abc", encriptar("abc"))` es `True`.

## Fase 2 — Clases base de repositorio (todo el SQL)
- [ ] `base_repositorio_postgresql.py`: engine lazy, helpers de tipos
      (`_detectar_tipo_columna`, `_convertir_valor`, `_serializar_valor`, fechas)
      y las 6 operaciones **públicas + alias `_` protegidos** (plan §5).
- [ ] `base_repositorio_mysql_mariadb.py` (backticks, sin esquema default,
      conversor de cadena estilo C# → URL).
- [ ] `base_repositorio_sqlserver.py` (corchetes, `TOP (n)` con `limite`
      validado como int, esquema `dbo`, conversor ODBC → URL).
- [ ] `repositorios/abstracciones/i_repositorio_lectura_tabla.py` y los alias
      `RepositorioLectura* = Base*` en `repositorios/__init__.py`.

**Verificar:** script suelto: `BaseRepositorioPostgreSQL(ProveedorConexion())`
lista `producto` (8 filas serializables a JSON) y filtra `factura` por
`numero="1"` (conversión texto→int automática).

## Fase 3 — Corte vertical de PERSONA (el molde)
- [ ] `models/persona.py` ([5_data_model.md](5_data_model.md) §5).
- [ ] `repositorios/abstracciones/i_repositorio_persona.py` (Protocol, 5 métodos).
- [ ] `repositorios/persona/` con las 3 variantes (constantes `TABLA`/`CLAVE_PRIMARIA`
      + delegación; plan §6).
- [ ] `servicios/abstracciones/i_servicio_persona.py` + `servicios/servicio_persona.py`.
- [ ] `_REPOS_PERSONA` + `crear_servicio_persona()` en `fabrica_repositorios.py` (plan §7).
- [ ] `controllers/persona_controller.py` (5 endpoints, patrón del plan §8).
- [ ] `main.py` mínimo registrando solo persona + endpoint `/`.

**Verificar:** `uvicorn main:app --port 8002` → en `/docs`: listar (200),
P001 (200), NOEXISTE (404), POST sin `nombre` (422), ciclo crear/editar/eliminar
de P999. Repetir con `DB_PROVIDER=mariadb`.

## Fase 4 — Entidades simples (replicar el molde ×6)
- [ ] empresa, producto (PK codigo) · cliente, vendedor, rol (PK serial) ·
      factura (PK numero) — cada una: modelo + interfaz + 3 repos + servicio +
      interfaz de servicio + entrada en fábrica + controller + registro en main.

**Verificar:** 7 tags en `/docs`; `GET /api/factura/1` → fecha ISO y total 5000000;
`POST /api/cliente/` sin `id` crea con serial; FK violada → 500 con detalle.

## Fase 5 — Usuario con BCrypt
- [ ] Repositorios de usuario con `CAMPOS_ENCRIPTAR = "contrasena"` y el método
      extra `obtener_hash_contrasena`.
- [ ] `ServicioUsuario.verificar_contrasena()` → `(200|401|404, mensaje)`.
- [ ] Controller: CRUD + `POST /api/usuario/verificar-contrasena`.

**Verificar:** [7_quickstart.md](7_quickstart.md) §3 paso 5 completo
(hash `$2b$12$…` de 60 chars en la BD; 200/401/404 según el caso).

## Fase 6 — Ruta y tablas puente
- [ ] `ruta`: CRUD con `{valor_ruta:path}` en los endpoints con parámetro.
- [ ] `productosporfactura`: sin PUT; `GET /factura/{fknumfactura}`; DELETE por
      PK compuesta — **aplicar la decisión de la spec RF2** (ambas columnas o
      réplica fiel) y dejarla comentada en el código.
- [ ] `rol_usuario` (prefix `/api/rol-usuario`) y `rutarol`: sin PUT, búsquedas
      secundarias, misma decisión en el DELETE.

**Verificar:** `GET /api/ruta//home` (200); quickstart §3 paso 6 (el trigger
recalcula stock/total); `GET /api/rol-usuario/usuario/admin@correo.com` lista roles.

## Fase 7 — Controller genérico de respaldo
- [ ] `servicios/servicio_crud.py` sobre `IRepositorioLecturaTabla`.
- [ ] `controllers/entidades_controller.py` (6 endpoints, mapeo de excepciones
      ampliado; [6_contracts.md](6_contracts.md) §3).
- [ ] Registrarlo **de último** en `main.py`.

**Verificar:** `GET /api/persona/` sigue llegando al controller específico;
crear una tabla de prueba a mano en la BD y consultarla por `/api/{tabla}` (200).

## Fase 8 — Docker y cierre
- [ ] `Dockerfile` (plan §1) — build y run standalone.
- [ ] `CORSMiddleware` si se adoptó la mejora RNF6.
- [ ] Si se integra al proyecto padre: alta en su compose (servicio
      `api-facturas`, puerto 8002, volumen de código + `--reload`, variables `DB_*`).

**Verificar:** [7_quickstart.md](7_quickstart.md) completo con los 3 motores —
equivale a los 10 criterios de aceptación de [2_spec.md](2_spec.md) §6.
