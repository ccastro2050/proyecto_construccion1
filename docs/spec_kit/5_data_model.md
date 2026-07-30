# Modelo de datos — bdfacturas (los 3 motores)

> **Documento 5 de 8** del spec kit raíz. La misma base de datos existe en tres
> dialectos: `db/postgres/init.sql` · `db/mariadb/init.sql` · `db/sqlserver/bdfacturas.sql`
> (+ `db/sqlserver/init.sh`). Este documento define el contenido común y las
> particularidades por dialecto.

---

## 1. Las 12 tablas (orden de creación = orden de dependencias)

**Independientes:**

| Tabla | Columnas (todas NOT NULL salvo indicado) |
|---|---|
| `empresa` | `codigo VARCHAR(10) PK` · `nombre VARCHAR(100)` |
| `persona` | `codigo VARCHAR(10) PK` · `nombre VARCHAR(100)` · `email VARCHAR(100)` · `telefono VARCHAR(20)` |
| `producto` | `codigo VARCHAR(10) PK` · `nombre VARCHAR(100)` · `stock INTEGER` · `valorunitario NUMERIC` |
| `rol` | `id SERIAL PK` · `nombre VARCHAR(50)` |
| `ruta` | `id SERIAL PK` · `ruta VARCHAR(100) UNIQUE` · `descripcion VARCHAR(200)` |
| `usuario` | `email VARCHAR(100) PK` · `contrasena VARCHAR(200)` (hash BCrypt) |

**Dependientes:**

| Tabla | Columnas y FK |
|---|---|
| `cliente` | `id SERIAL PK` · `credito NUMERIC DEFAULT 0` · `fkcodpersona → persona.codigo` · `fkcodempresa → empresa.codigo` (NULL permitido) |
| `vendedor` | `id SERIAL PK` · `carnet INTEGER` · `direccion VARCHAR(100)` · `fkcodpersona → persona.codigo` |
| `factura` | `numero SERIAL PK` · `fecha TIMESTAMP DEFAULT now` · `total NUMERIC DEFAULT 0` · `estado VARCHAR(10) DEFAULT 'activa'` · `fkidcliente → cliente.id` · `fkidvendedor → vendedor.id` |
| `productosporfactura` | **PK (fknumfactura, fkcodproducto)** · `fknumfactura → factura.numero ON DELETE CASCADE` · `fkcodproducto → producto.codigo` · `cantidad INTEGER` · `subtotal NUMERIC DEFAULT 0` |
| `rol_usuario` | **PK (fkemail, fkidrol)** · `fkemail → usuario.email` · `fkidrol → rol.id` |
| `rutarol` | **PK (fkidruta, fkidrol)** · ambas FK con `ON DELETE CASCADE` |

## 2. Trigger `actualizar_totales_y_stock`

BEFORE INSERT/UPDATE/DELETE en `productosporfactura`:
- **INSERT:** valida stock suficiente (excepción si falta), `subtotal :=
  cantidad × valorunitario`, descuenta stock, recalcula total de la factura.
- **UPDATE:** ídem considerando la devolución del stock anterior.
- **DELETE:** restaura stock y recalcula total.

## 3. Procedimientos almacenados (~15, retornan JSON)

| Grupo | SP |
|---|---|
| Facturas | `sp_insertar_factura_y_productosporfactura` (recibe cliente, vendedor y JSON de productos; el trigger hace los cálculos) · `sp_consultar_…` (con nombres de cliente/vendedor) · `sp_listar_…` · `sp_actualizar_…` (reemplaza el detalle) · `sp_borrar_…` (físico, CASCADE) · `sp_anular_factura` (lógico: estado='anulada' + restaurar stock) |
| Usuarios | `crear_usuario_con_roles` · `actualizar_usuario_con_roles` · `eliminar_usuario_con_roles` · `actualizar_roles_usuario` · `consultar_usuario_con_roles` · `listar_usuarios_con_roles` |
| RBAC | `verificar_acceso_ruta` (¿el usuario alcanza la ruta por sus roles?) · `listar_rutarol` · `crear_rutarol` · `eliminar_rutarol` |

En PostgreSQL: `CREATE PROCEDURE` con parámetro `INOUT p_resultado JSON`
(requiere PG 11+). En MariaDB/SQL Server: equivalentes con OUT/SELECT.

## 4. Datos de ejemplo (idénticos en los 3 motores)

3 empresas (E001, E002, E999) · 6 personas (P001 Ana Torres … P006 Pedro
Castillo) · 8 productos (PR001 Laptop Lenovo $2.500.000 stock 17 … PR008) ·
5 roles (Administrador, Vendedor, Cajero, Contador, Cliente) · 15 rutas ·
8 usuarios (admin@correo.com y otros con hash BCrypt; dos con clave en texto
plano como material didáctico de "lo que NO se hace") · 4 clientes (ids 1,2,3,5) ·
3 vendedores · 6 facturas · 12 renglones de detalle · 21 rol_usuario ·
25 rutarol (el rol 1 tiene las 15 rutas).

En PostgreSQL, tras insertar con id explícito: `setval` de las secuencias de
rol, cliente, vendedor y factura.

## 5. Particularidades por dialecto

| Aspecto | PostgreSQL (`db/postgres/init.sql`) | MariaDB (`db/mariadb/init.sql`) | SQL Server (`db/sqlserver/`) |
|---|---|---|---|
| Autoincremento | `SERIAL` + `setval` | `AUTO_INCREMENT` | `IDENTITY` + `SET IDENTITY_INSERT` |
| Trigger/SP | `plpgsql`, JSON nativo | `DELIMITER //`, JSON como texto | T-SQL, `FOR JSON` |
| Re-ejecutable | No hace falta (solo corre con volumen vacío) | `DROP … IF EXISTS` de todo + `CREATE DATABASE IF NOT EXISTS` + `SET NAMES utf8mb4` | `init.sh` verifica `sys.databases` antes de crear |
| Ejecución | entrypoint oficial (`/docker-entrypoint-initdb.d`) | entrypoint oficial | `sqlserver-init` con `sqlcmd -i` |

**Regla de oro:** los 3 scripts deben producir el MISMO estado observable
(mismas filas, mismos cálculos del trigger, mismos resultados de SP). Cualquier
cambio de esquema se hace en los 3 a la vez.
