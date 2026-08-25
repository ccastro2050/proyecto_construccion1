# Modelo de datos — API Facturas

> **Documento 5 de 8** del spec kit ([2_spec.md](2_spec.md) · [3_plan.md](3_plan.md) ·
> [6_contracts.md](6_contracts.md) · [8_tasks.md](8_tasks.md)). La API es un proyecto
> independiente: su única dependencia externa es una base de datos `bdfacturas`
> con este esquema. El DDL completo de referencia (PostgreSQL) vive en
> `api_facturas/database/bdfacturas_postgres.sql`.

---

## 1. Diagrama de dependencias

```
empresa ─┐
persona ─┼─→ cliente ──┐
persona ──→ vendedor ──┼─→ factura ──→ productosporfactura ←── producto
usuario ─┬─→ rol_usuario ←── rol
ruta ────┴─→ rutarol   ←── rol
```

## 2. Las 12 tablas

### Tablas independientes (sin FK)

| Tabla | Columnas | Restricciones |
|---|---|---|
| `empresa` | `codigo VARCHAR(10)` · `nombre VARCHAR(100)` | PK `codigo`; todo NOT NULL |
| `persona` | `codigo VARCHAR(10)` · `nombre VARCHAR(100)` · `email VARCHAR(100)` · `telefono VARCHAR(20)` | PK `codigo`; todo NOT NULL |
| `producto` | `codigo VARCHAR(10)` · `nombre VARCHAR(100)` · `stock INTEGER` · `valorunitario NUMERIC` | PK `codigo`; todo NOT NULL |
| `rol` | `id SERIAL` · `nombre VARCHAR(50)` | PK `id` |
| `ruta` | `id SERIAL` · `ruta VARCHAR(100)` · `descripcion VARCHAR(200)` | PK `id`; UNIQUE `ruta` |
| `usuario` | `email VARCHAR(100)` · `contrasena VARCHAR(200)` | PK `email`; la contraseña se guarda como hash BCrypt (60 chars) |

### Tablas dependientes (con FK)

| Tabla | Columnas | Restricciones |
|---|---|---|
| `cliente` | `id SERIAL` · `credito NUMERIC DEFAULT 0` · `fkcodpersona VARCHAR(10)` · `fkcodempresa VARCHAR(10) NULL` | PK `id`; FK → persona.codigo, empresa.codigo |
| `vendedor` | `id SERIAL` · `carnet INTEGER` · `direccion VARCHAR(100)` · `fkcodpersona VARCHAR(10)` | PK `id`; FK → persona.codigo |
| `factura` | `numero SERIAL` · `fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP` · `total NUMERIC DEFAULT 0` · `estado VARCHAR(10) DEFAULT 'activa'` · `fkidcliente INTEGER` · `fkidvendedor INTEGER` | PK `numero`; FK → cliente.id, vendedor.id |
| `productosporfactura` | `fknumfactura INTEGER` · `fkcodproducto VARCHAR(10)` · `cantidad INTEGER` · `subtotal NUMERIC DEFAULT 0` | **PK compuesta** (fknumfactura, fkcodproducto); FK → factura.numero **ON DELETE CASCADE**, producto.codigo |
| `rol_usuario` | `fkemail VARCHAR(100)` · `fkidrol INTEGER` | **PK compuesta**; FK → usuario.email, rol.id |
| `rutarol` | `fkidruta INT` · `fkidrol INT` | **PK compuesta**; FK → ruta.id, rol.id, ambas **ON DELETE CASCADE** |

## 3. Lógica que vive en la base de datos (NO en la API)

La API es deliberadamente "tonta" respecto a facturación: subtotales, totales y
stock los calcula la BD.

- **Trigger `actualizar_totales_y_stock`** (BEFORE INSERT/UPDATE/DELETE en
  `productosporfactura`): valida stock suficiente (si no, lanza excepción),
  calcula `subtotal = cantidad × valorunitario`, descuenta/restaura `stock` del
  producto y recalcula `total` de la factura.
- **Procedimientos almacenados** (retornan JSON):
  facturas (`sp_insertar/consultar/listar/actualizar/borrar_factura_y_productosporfactura`,
  `sp_anular_factura` = borrado lógico con restauración de stock), usuarios con
  roles (`crear/actualizar/eliminar/consultar/listar_usuarios_con_roles`,
  `actualizar_roles_usuario`) y RBAC (`verificar_acceso_ruta`, `listar/crear/eliminar_rutarol`).

Consecuencia para la API: al insertar un `productosporfactura` con `subtotal: 0`,
la BD lo corrige sola; un error de stock insuficiente llega a la API como
excepción del motor → HTTP 500 con el mensaje del trigger en `detalle`.

## 4. Datos de ejemplo (para los criterios de aceptación)

| Tabla | Registros | Muestras |
|---|---|---|
| empresa | 3 | E001 Comercial Los Andes S.A. |
| persona | 6 | P001 Ana Torres · P002 Carlos Pérez … P006 Pedro Castillo |
| producto | 8 | PR001 Laptop Lenovo IdeaPad ($2.500.000, stock 17) … PR008 |
| rol | 5 | 1 Administrador · 2 Vendedor · 3 Cajero · 4 Contador · 5 Cliente |
| ruta | 15 | /home, /usuario, /factura, … |
| usuario | 8 | admin@correo.com (hash BCrypt) … |
| cliente | 4 | ids 1,2,3,5 |
| vendedor | 3 | ids 1,2,3 |
| factura | 6 | números 1–6 |
| productosporfactura | 12 | factura 1: PR001×2 … |
| rol_usuario / rutarol | 21 / 25 | admin con rol 1; rol 1 con las 15 rutas |

Tras insertar con ids explícitos, PostgreSQL requiere sincronizar secuencias
(`setval` en rol, cliente, vendedor, factura).

## 5. Modelos Pydantic (capa `models/`)

Un archivo por entidad, clases `BaseModel` planas (sin `Field`, sin validadores
custom, sin `model_config`). Los modelos son **más laxos que el DDL** a propósito:
columnas NOT NULL con default en BD se modelan opcionales; la BD es la última
línea de defensa.

```python
class Persona(BaseModel):
    codigo: str                      # PK
    nombre: str
    email: str | None = None
    telefono: str | None = None

class Empresa(BaseModel):
    codigo: str                      # PK
    nombre: str

class Cliente(BaseModel):
    id: int | None = None            # SERIAL — no se envía al crear
    credito: float | None = None
    fkcodpersona: str                # FK → persona.codigo
    fkcodempresa: str                # FK → empresa.codigo

class Vendedor(BaseModel):
    id: int | None = None            # SERIAL
    carnet: int | None = None
    direccion: str | None = None
    fkcodpersona: str                # FK → persona.codigo

class Producto(BaseModel):
    codigo: str                      # PK
    nombre: str
    stock: int | None = None
    valorunitario: float | None = None

class Factura(BaseModel):
    numero: int | None = None        # SERIAL
    fecha: str | None = None         # timestamp como texto ISO
    total: float | None = None       # lo calcula el trigger
    fkidcliente: int                 # FK → cliente.id
    fkidvendedor: int                # FK → vendedor.id

class ProductosPorFactura(BaseModel):
    fknumfactura: int                # PK compuesta 1/2 + FK → factura.numero
    fkcodproducto: str               # PK compuesta 2/2 + FK → producto.codigo
    cantidad: int
    subtotal: float | None = None    # lo calcula el trigger

class Usuario(BaseModel):
    email: str                       # PK
    contrasena: str                  # se guarda como hash BCrypt

class Rol(BaseModel):
    id: int | None = None            # SERIAL
    nombre: str

class RolUsuario(BaseModel):
    fkemail: str                     # PK compuesta + FK → usuario.email
    fkidrol: int                     # PK compuesta + FK → rol.id

class Ruta(BaseModel):
    ruta: str                        # PK lógica usada por la API (contiene '/')
    descripcion: str | None = None

class RutaRol(BaseModel):
    ruta: str                        # PK compuesta
    rol: str                         # PK compuesta
```

`models/__init__.py` exporta las 12 clases y un mapa auxiliar:

```python
MODELOS_POR_TABLA = {"persona": Persona, "empresa": Empresa, "cliente": Cliente,
    "vendedor": Vendedor, "producto": Producto, "factura": Factura,
    "productosporfactura": ProductosPorFactura, "usuario": Usuario, "rol": Rol,
    "rol_usuario": RolUsuario, "ruta": Ruta, "rutarol": RutaRol}
```

## 6. Cómo montar la BD (un contenedor por motor, el que se vaya a usar)

Los scripts de los 3 motores vienen incluidos en `database/`
(`bdfacturas_postgres.sql`, `bdfacturas_mariadb.sql`, `bdfacturas_sqlserver.sql`):

```powershell
docker run -d --name bdfacturas -p 15448:5432 `
  -e POSTGRES_DB=bdfacturas_postgres_local `
  -e POSTGRES_USER=paradigmas -e POSTGRES_PASSWORD=paradigmas123 `
  -v ${PWD}/database/bdfacturas_postgres.sql:/docker-entrypoint-initdb.d/init.sql:ro `
  postgres:16-alpine
```

Para MariaDB (`mariadb:11`, puerto sugerido 13316) y SQL Server
(`mssql/server:2022`, puerto sugerido 11443) el patrón es el mismo con su
script correspondiente.

Cadena de conexión resultante para la API:
`DB_POSTGRES=postgresql+asyncpg://paradigmas:paradigmas123@localhost:15448/bdfacturas_postgres_local`
