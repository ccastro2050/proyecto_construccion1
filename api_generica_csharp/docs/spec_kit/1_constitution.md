# Constitución — API Genérica C# (ASP.NET Core)

> **Documento 1 de 8** del spec kit. Orden de lectura:
> `1_constitution → 2_spec → 3_plan → 4_research → 5_data_model → 6_contracts → 7_quickstart → 8_tasks`.
>
> Principios innegociables de este proyecto. El spec kit es **autocontenido**:
> con esta carpeta se reconstruye la API completa desde cero, sin depender de
> ningún otro proyecto o documento externo.

---

## Artículo 1 — Propósito didáctico

Proyecto para enseñar a estudiantes qué es una API genérica en C# / ASP.NET
Core: **un solo conjunto de endpoints que sirve para cualquier tabla**, sin
conocer sus columnas de antemano, más autenticación JWT y ejecución segura de
consultas y procedimientos almacenados. Claridad sobre sofisticación:

- Código y comentarios en **español**, con intención de tutorial: cada archivo
  abre con un encabezado que explica su papel y sus principios SOLID.
- Los comentarios XML (`///`) alimentan Swagger y sirven de material de clase.
- El SQL queda **visible** (Dapper/ADO.NET con SQL a mano, nada de Entity
  Framework que lo esconda).

## Artículo 2 — Genericidad radical

- CERO conocimiento del esquema: ni nombres de tablas ni de columnas en el código.
- Cada fila viaja como `Dictionary<string, object?>` — las columnas se descubren
  en runtime.
- Única excepción de conocimiento del dominio: la **lista de tablas prohibidas**
  (`TablasProhibidas` en `appsettings.json`), que es configuración, no código.
- El precio asumido y documentado: sin validación por entidad, la BD es la
  única línea de defensa sobre columnas y tipos.

## Artículo 3 — Arquitectura en capas estricta

```
HTTP → CONTROLLER (traduce excepciones a códigos HTTP; no toca SQL)
     → SERVICIO   (reglas de negocio y política de tablas; ignora HTTP y motor)
     → REPOSITORIO(un dialecto SQL por clase; ignora HTTP)
     → BASE DE DATOS
```

Comunicación entre capas por **interfaces** (`interface` de C#); solo
`Program.cs` (el contenedor de inyección de dependencias) conoce las clases
concretas — el registro condicional en el contenedor cumple el papel de fábrica.

## Artículo 4 — Independencia del motor

- Motor elegido con la configuración `DatabaseProvider`, jamás con cambios de
  código.
- Un repositorio por dialecto (PostgreSQL, MySQL/MariaDB, SQL Server); agregar
  un motor = 2 clases + 1 `case` en el `switch` de `Program.cs`.
- Los tres motores se comportan **idéntico** ante la misma petición.

## Artículo 5 — Seguridad en su justa medida académica

- Valores SQL SIEMPRE parametrizados (`@param`); los identificadores van entre
  las comillas del dialecto (`"`, `` ` ``, `[]`).
- Contraseñas SIEMPRE como hash BCrypt (costo 10) cuando el cliente lo pide
  (`camposEncriptar`); verificación server-side.
- **JWT real**: `POST /api/Autenticacion/token` emite tokens HS256 y
  `GET /api/{tabla}` exige `[Authorize]` — suficiente para enseñar el mecanismo
  sin bloquear el resto de la API (los demás endpoints son `[AllowAnonymous]`
  a propósito).
- Solo consultas **SELECT** en `/api/consultas`; las tablas de
  `TablasProhibidas` se rechazan con 403.

## Artículo 6 — Convenciones fijas

| Cosa | Convención |
|---|---|
| Puerto | **8013** |
| Docs | `/swagger` (Swashbuckle) y `/redoc`; OpenAPI en `/swagger/v1/swagger.json` |
| Rutas | `/api/{tabla}` (entidades) · `/api/autenticacion` · `/api/consultas` · `/api/procedimientos` · `/api/estructuras` · `/api/diagnostico` |
| Nombres | PascalCase en español; interfaces con prefijo `I`; carpetas `Controllers/ Servicios/ Repositorios/ Modelos/` |
| Sobre de respuesta | `{tabla, esquema, total, datos}` / `{estado, mensaje, detalle, …}` — ver 6_contracts.md |
| Errores | `ArgumentException`→400 · `UnauthorizedAccessException`→403 · `InvalidOperationException`→404 (lecturas) o 500 (escrituras) · resto→500 |
