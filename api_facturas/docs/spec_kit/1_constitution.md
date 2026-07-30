# Constitución — API Facturas

> **Documento 1 de 8** del spec kit. Orden de lectura:
> `1_constitution → 2_spec → 3_plan → 4_research → 5_data_model → 6_contracts → 7_quickstart → 8_tasks`.
>
> Principios innegociables de ESTE proyecto tratado como independiente. Si se
> construye dentro del proyecto padre (proyecto_paradigmas), aplica además la
> constitución global en `docs/spec_kit/1_constitution.md` de la raíz.

---

## Artículo 1 — Propósito didáctico

El proyecto existe para enseñar arquitectura en capas y validación tipada a
estudiantes universitarios. Ante la disyuntiva entre "lo más profesional" y
"lo más claro para aprender", gana la claridad:

- Todo en **español**: código, comentarios, docstrings, mensajes, documentación.
- Cada archivo abre con un docstring que explica su papel en la arquitectura.
- Se prefiere código explícito y repetido-pero-legible (12 cortes verticales
  casi idénticos) sobre metaprogramación compacta.

## Artículo 2 — Arquitectura en capas estricta

```
HTTP → CONTROLLER (valida entrada, traduce errores a códigos HTTP)
     → SERVICIO   (valida argumentos, normaliza; ignora HTTP y SQL)
     → REPOSITORIO(habla el SQL de UN motor; ignora HTTP)
     → BASE DE DATOS
```

- Un controller **nunca** ejecuta SQL; un repositorio **nunca** lanza `HTTPException`.
- Las capas se comunican por **interfaces** (`typing.Protocol`), no por clases
  concretas: inversión de dependencias (la D de SOLID).
- Solo la **fábrica** conoce las clases concretas de repositorio (patrón Factory,
  principio abierto/cerrado: motor nuevo = repos nuevos + 1 entrada al diccionario).

## Artículo 3 — Un CRUD por entidad, validado

Cada una de las 12 entidades tiene su corte vertical completo: modelo Pydantic +
interfaz + 3 repositorios + servicio + controller. La validación de tipos ocurre
en el borde (Pydantic → 422 automático). Esta API es el contraste pedagógico de
una API genérica sin validación por entidad: aquí se paga más código a cambio de
contratos explícitos.

## Artículo 4 — Independencia del motor de base de datos

- El motor se elige con `DB_PROVIDER` (`postgres` | `mariadb`/`mysql` |
  `sqlserver`), jamás con cambios de código.
- Todo el SQL de un dialecto vive en UNA clase base; los repositorios de entidad
  no contienen SQL.
- Los tres motores deben comportarse **idéntico** ante la misma petición.

## Artículo 5 — La lógica de facturación vive en la base de datos

Subtotales, totales y stock los calculan el trigger y los procedimientos
almacenados de `bdfacturas`. La API no los reimplementa ni los "corrige".
Un error del trigger (stock insuficiente) se propaga al cliente con su mensaje.

## Artículo 6 — Seguridad en su justa medida académica

- Contraseñas SIEMPRE como hash BCrypt (costo 12); nunca texto plano en código nuevo.
- Valores SQL SIEMPRE parametrizados (`:param`), nunca concatenados.
- Sin autenticación de API ni secretos reales: este entorno no va a producción.

## Artículo 7 — Convenciones fijas

| Cosa | Convención |
|---|---|
| Puerto | **8002** |
| Docs | `/docs` (Swagger UI, default de FastAPI) y `/redoc` |
| Nombres | snake_case en español; clases PascalCase; interfaces `i_`/`I` |
| Sufijos de motor | `_postgresql` · `_mysql_mariadb` · `_sqlserver` |
| Constantes de clase | `TABLA`, `CLAVE_PRIMARIA`, `CAMPOS_ENCRIPTAR` |
| Sobre de respuesta | `{tabla, total, datos}` / `{estado, mensaje, …}` — ver 6_contracts.md |
| Registro de routers | los 12 específicos primero, el genérico de último |
