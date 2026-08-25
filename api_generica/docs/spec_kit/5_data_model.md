# Modelo de datos — API Genérica CRUD

> **Documento 5 de 8** del spec kit. **Nota:** esta API es agnóstica del esquema
> — NO tiene modelos propios ni conoce tabla alguna. Este documento describe
> (a) lo que la API descubre en runtime y (b) la base de datos de prueba
> `bdfacturas` con la que se validan los criterios de aceptación.

---

## 1. Lo que la API "sabe" de los datos (nada, hasta runtime)

- **Tablas:** el nombre llega en la URL (`/api/{tabla}`); no hay lista blanca.
- **Columnas:** las descubre el `SELECT *` (las claves del dict de cada fila).
- **Tipos:** los consulta en `information_schema.columns` cuando necesita
  convertir un valor que llegó como texto:

| Tipo en el catálogo | Conversión Python |
|---|---|
| integer, int4, bigint, int8, smallint, int2 | `int(valor)` |
| numeric, decimal | `Decimal(valor)` |
| real, float4, double precision, float8 | `float(valor)` |
| boolean, bool | `valor.lower() in ('true','1','yes','si','t')` |
| uuid | `UUID(valor)` |
| date | `date.fromisoformat` (o parte fecha de un ISO) |
| timestamp (con/sin zona) | `datetime.fromisoformat` (`Z` → `+00:00`) |
| time | `time.fromisoformat` |
| cualquier otro / conversión fallida | el string tal cual |

- **Serialización de salida:** `datetime/date` → ISO 8601, `Decimal` → float,
  `UUID` → str (todo lo demás pasa directo a JSON).

## 2. Base de datos de prueba: `bdfacturas`

Para construir y validar la API se usa una BD de facturación (12 tablas, datos
de ejemplo, trigger de totales/stock y SP) cuyos scripts para los 3 motores
vienen **incluidos en este proyecto**, en `database/`
(`bdfacturas_postgres.sql`, `bdfacturas_mariadb.sql`, `bdfacturas_sqlserver.sql`).
No es un requisito de la API — funciona contra cualquier BD — pero los
criterios de aceptación de [2_spec.md](2_spec.md) §5 se expresan sobre ella.

### Esquema resumido

**Independientes:** `empresa(codigo PK, nombre)` · `persona(codigo PK, nombre,
email, telefono)` · `producto(codigo PK, nombre, stock INT, valorunitario NUMERIC)` ·
`rol(id SERIAL PK, nombre)` · `ruta(id SERIAL PK, ruta UNIQUE, descripcion)` ·
`usuario(email PK, contrasena)` — contraseña como hash BCrypt.

**Con FK:** `cliente(id SERIAL PK, credito, fkcodpersona→persona, fkcodempresa→empresa)` ·
`vendedor(id SERIAL PK, carnet, direccion, fkcodpersona→persona)` ·
`factura(numero SERIAL PK, fecha TIMESTAMP, total, estado, fkidcliente→cliente,
fkidvendedor→vendedor)` · `productosporfactura(PK compuesta fknumfactura→factura
ON DELETE CASCADE + fkcodproducto→producto, cantidad, subtotal)` ·
`rol_usuario(PK compuesta fkemail→usuario + fkidrol→rol)` ·
`rutarol(PK compuesta fkidruta→ruta + fkidrol→rol, ambas CASCADE)`.

**Lógica en BD:** trigger `actualizar_totales_y_stock` en `productosporfactura`
(valida stock, calcula subtotal, ajusta stock, recalcula total) y ~15 SP de
facturas/usuarios/RBAC. Importa para esta API: un INSERT genérico en
`productosporfactura` dispara el trigger, y sus errores llegan como 500 con el
mensaje del motor en `detalle`.

### Datos de ejemplo relevantes

3 empresas · 6 personas (P001 Ana Torres…) · 8 productos (PR001 Laptop Lenovo…) ·
5 roles · 15 rutas · 8 usuarios (admin@correo.com con hash BCrypt) · 4 clientes ·
3 vendedores · 6 facturas · 12 renglones de detalle.

### Cómo montarla (un contenedor por motor, el que se vaya a usar)

El script incluido en `database/` montado en un contenedor (desde la raíz de
este proyecto):

```powershell
docker run -d --name bdfacturas -p 15448:5432 `
  -e POSTGRES_DB=bdfacturas_postgres_local `
  -e POSTGRES_USER=paradigmas -e POSTGRES_PASSWORD=paradigmas123 `
  -v ${PWD}/database/bdfacturas_postgres.sql:/docker-entrypoint-initdb.d/init.sql:ro `
  postgres:16-alpine
```

Para MariaDB (`mariadb:11`, puerto sugerido 13316) y SQL Server
(`mssql/server:2022`, puerto sugerido 11443) el patrón es el mismo con su
script de `database/` correspondiente.

Cadena para la API:
`DB_POSTGRES=postgresql+asyncpg://paradigmas:paradigmas123@localhost:15448/bdfacturas_postgres_local`

## 3. Advertencia de alcance

Como no hay modelos, **la BD es la única validación**: un POST con columnas
inexistentes o tipos incompatibles produce 500 con el error del motor. Esto es
una decisión pedagógica documentada ([4_research.md](4_research.md) D1), no un
descuido.
