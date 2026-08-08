# Modelo de datos — API Genérica C# (ASP.NET Core)

> **Documento 5 de 8** del spec kit. **Nota:** esta API es agnóstica del esquema
> — NO tiene modelos por tabla. Sus únicos "modelos" son de configuración
> (`ConfiguracionJwt`) y de transporte (`CredencialesGenericas`). Este documento
> describe (a) lo que la API descubre en runtime y (b) la BD de prueba
> `bdfacturas` con la que se validan los criterios de aceptación.

---

## 1. Lo que la API "sabe" de los datos (nada, hasta runtime)

- **Tablas:** el nombre llega en la URL (`/api/{tabla}`); no hay lista blanca —
  solo la lista **negra** opcional `TablasProhibidas` de `appsettings.json`.
- **Columnas:** las descubre el `SELECT *`; cada fila viaja como
  `Dictionary<string, object?>` (clave = columna, valor = dato o `null`).
- **Tipos de entrada:** dos direcciones de conversión:
  - **Body JSON → SQL:** `JsonElement` → `string` / `int` / `double` / `bool` /
    `null` (`ConvertirJsonElement`, antes de armar parámetros).
  - **URL → columna:** el valor de `/{nombreClave}/{valor}` llega como texto;
    el repositorio consulta el catálogo del motor y castea. Caso especial:
    valor `YYYY-MM-DD` sobre columna fecha/hora compara `CAST(col AS DATE)`.
- **Salida:** `DBNull.Value` → `null`; en consultas y SPs los nombres de columna
  se normalizan a **minúsculas**; los `DataTable` se aplanan a listas de
  diccionarios antes de serializar a JSON.

## 2. Modelos propios (los únicos dos)

| Clase | Campos | Papel |
|---|---|---|
| `ConfiguracionJwt` (Modelos/) | `Key`, `Issuer`, `Audience`, `DuracionMinutos` | Bind de la sección `Jwt` de appsettings; firma y validación de tokens |
| `CredencialesGenericas` (en AutenticacionController) | `Tabla`, `CampoUsuario`, `CampoContrasena`, `Usuario`, `Contrasena` | Body del `POST /api/Autenticacion/token` — genérico: sirve para cualquier tabla de usuarios |

## 3. Base de datos de prueba: `bdfacturas`

Una BD de facturación con 12 tablas, trigger de totales/stock y ~15 SPs. Sus
scripts para los tres motores vienen **incluidos en este proyecto**, en
`script_bd/` (`bdfacturas_postgres.sql`, `bdfacturas_mysql_mariadb.sql`,
`bdfacturas_sqlserver.sql`). No es requisito de la API — funciona contra
cualquier BD — pero los criterios de aceptación de [2_spec.md](2_spec.md) §5 se
expresan sobre ella.

### Esquema resumido

**Independientes:** `empresa(codigo PK, nombre)` · `persona(codigo PK, nombre,
email, telefono)` · `producto(codigo PK, nombre, stock INT, valorunitario NUMERIC)` ·
`rol(id SERIAL PK, nombre)` · `ruta(id SERIAL PK, ruta UNIQUE, descripcion)` ·
`usuario(email PK, contrasena)` — contraseña como hash BCrypt.

**Con FK:** `cliente(id, credito, fkcodpersona→persona, fkcodempresa→empresa)` ·
`vendedor(id, carnet, direccion, fkcodpersona→persona)` ·
`factura(numero, fecha TIMESTAMP, total, estado, fkidcliente, fkidvendedor)` ·
`productosporfactura(PK compuesta fknumfactura+fkcodproducto, cantidad, subtotal)` ·
`rol_usuario(fkemail+fkidrol)` · `rutarol(fkidruta+fkidrol)`.

**Lógica en BD:** trigger `actualizar_totales_y_stock` en `productosporfactura`
y ~15 SPs (facturación, usuarios con roles, RBAC) que devuelven JSON — estos
últimos son el material ideal para `POST /api/procedimientos/ejecutarsp`.

### Datos de ejemplo relevantes

8 productos (PR001 Laptop Lenovo…) · 6 personas · 8 usuarios — para el JWT
importa: **`admin@correo.com` con contraseña `admin123`** (hash BCrypt en la
tabla `usuario`).

### Cómo montarla (un contenedor por motor, el que se vaya a usar)

```powershell
# Desde la raíz de este proyecto (usa el script incluido en script_bd/):
docker run -d --name bdfacturas -p 15442:5432 `
  -e POSTGRES_DB=bdfacturas_postgres_local `
  -e POSTGRES_USER=paradigmas -e POSTGRES_PASSWORD=paradigmas123 `
  -v ${PWD}/script_bd/bdfacturas_postgres.sql:/docker-entrypoint-initdb.d/init.sql:ro `
  postgres:16-alpine
```

Cadena para `appsettings.json` (o `ConnectionStrings__Postgres`):
`Host=localhost;Port=15442;Database=bdfacturas_postgres_local;Username=paradigmas;Password=paradigmas123;`

Para MariaDB (`mariadb:11`, puerto sugerido 13316) y SQL Server
(`mssql/server:2022`, puerto sugerido 11443) el patrón es el mismo con su
script de `script_bd/` correspondiente.

## 4. Advertencia de alcance

Sin modelos por tabla, **la BD es la única validación** de columnas y tipos: un
POST con columnas inventadas produce 500 con el error del motor en `detalle`.
Es una decisión pedagógica documentada ([4_research.md](4_research.md) D1);
la única defensa adicional es `TablasProhibidas` (403).
