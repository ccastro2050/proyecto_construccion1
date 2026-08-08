# Modelo de datos — Front Blazor (Blazor Server)

> **Documento 5 de 8** del spec kit · **Informativo**: el front NO tiene base
> de datos propia ni modelos por tabla — consume todo vía la API. Este
> documento describe (a) los datos que maneja en memoria y (b) la BD de prueba
> `bdfacturas` contra la que se validan los criterios de aceptación.

---

## 1. Lo que el front "sabe" de los datos

- **Registros:** cada fila viaja como diccionario/JSON genérico; las columnas
  se descubren al listar (las claves del objeto).
- **Estructura:** al iniciar sesión, `AuthService.PrecargarEstructura()` pide a
  la API la estructura de la BD y **cachea las PKs y FKs** por tabla — con eso
  arma las URLs de actualizar/eliminar y los selects de FK.
- **Estado en memoria (por circuito/usuario):** `Usuario` (email), `Token`
  (JWT), `Roles` (lista), `RutasPermitidas` (lista), `DebeCambiarContrasena`
  (bool) — y su copia encriptada en `ProtectedSessionStorage`.

## 2. Base de datos de prueba: `bdfacturas`

Una BD de facturación (12 tablas, trigger de totales/stock, SPs) cuyos scripts
vienen **incluidos en este proyecto**, en `script_bd/`
(`bdfacturas_postgres.sql`, `bdfacturas_sqlserver.sql`). El front no la toca
directamente — la ve a través de la API — pero sus páginas CRUD están escritas
para estas tablas.

### Tablas de negocio (una página CRUD por cada una)

**Independientes:** `empresa(codigo PK, nombre)` · `persona(codigo PK, nombre,
email, telefono)` · `producto(codigo PK, nombre, stock INT, valorunitario NUMERIC)`.

**Con FK (los formularios usan selects):** `cliente(id, credito,
fkcodpersona→persona, fkcodempresa→empresa)` · `vendedor(id, carnet, direccion,
fkcodpersona→persona)` · `factura(numero, fecha, total, estado,
fkidcliente→cliente, fkidvendedor→vendedor)` · `productosporfactura(PK compuesta
fknumfactura+fkcodproducto, cantidad, subtotal)`.

**Lógica en la BD que el front respeta:** el trigger `actualizar_totales_y_stock`
calcula subtotal, descuenta stock y recalcula el total de la factura — por eso
la página de facturas **no** envía totales; y las FK con `NO ACTION` hacen que
eliminar un registro referenciado falle en la BD (el front solo muestra el error).

### Tablas de seguridad (las usa el control de acceso)

```
usuario(email PK, contrasena=hash BCrypt)
rol(id, nombre)                rol_usuario(fkemail, fkidrol)   ← roles de cada usuario
ruta(id, ruta UNIQUE, descripcion)   rutarol(fkidruta, fkidrol) ← rutas de cada rol
```

El login consulta `usuario` (BCrypt vía API) y luego arma, con JOINs sobre
estas 5 tablas, los `Roles` y `RutasPermitidas` de la sesión. **Un usuario sin
filas en `rol_usuario` no puede entrar** (mensaje "sin roles").

### Datos de ejemplo relevantes

8 productos (PR001 Laptop Lenovo…) · 8 usuarios — para probar:
**`admin@correo.com` / `admin123`** (hash BCrypt en la tabla), con roles que
permiten todas las rutas.

## 3. Cómo montar la BD (si no existe ya)

La API es quien se conecta; para el escenario más simple (PostgreSQL suelto):

```powershell
docker run -d --name bdfacturas -p 15442:5432 `
  -e POSTGRES_DB=bdfacturas_postgres_local `
  -e POSTGRES_USER=paradigmas -e POSTGRES_PASSWORD=paradigmas123 `
  -v ${PWD}/script_bd/bdfacturas_postgres.sql:/docker-entrypoint-initdb.d/init.sql:ro `
  postgres:16-alpine
```

y apuntar la API a esa BD (el front solo necesita `ApiBaseUrl`).

## 4. Advertencia de alcance

El front asume que la API valida y que la BD manda: un error de FK, de stock o
de PK duplicada llega como error HTTP y el front **solo lo muestra** — no
duplica reglas de negocio del lado del cliente (más allá de la validación de
formato de la contraseña nueva).
