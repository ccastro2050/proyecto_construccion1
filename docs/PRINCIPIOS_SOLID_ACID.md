# Principios SOLID y ACID — aplicados en este proyecto

No son teoría suelta: **cada principio está funcionando en un archivo concreto de este repositorio**. Este documento dice cuál y dónde verlo.

- **SOLID** → principios de diseño del **código** (viven en `api_generica/` y `api_facturas/`)
- **ACID** → propiedades de las **transacciones de la base de datos** (viven en los scripts de `db/`)

---

# Parte 1 — SOLID (diseño del código)

SOLID son cinco principios para que el código aguante el cambio: agregar cosas nuevas sin romper las que ya funcionan.

## S — Single Responsibility (Responsabilidad Única)

> *Cada clase/módulo debe tener UNA sola razón para cambiar.*

**Aplicado:** cada capa de las APIs hace UNA cosa:

| Carpeta | Su única responsabilidad | Cambia solo si… |
|---|---|---|
| `controllers/` | Recibir HTTP y retornar JSON | cambia el contrato de la API (rutas, códigos de estado) |
| `servicios/` | Reglas de negocio y validaciones | cambia una regla del negocio |
| `repositorios/` | Ejecutar SQL contra un motor | cambia la base de datos |
| `models/` (api_facturas) | Definir y validar la forma de los datos | cambia la estructura de una entidad |

**Véalo:** [api_facturas/controllers/persona_controller.py](../api_facturas/controllers/persona_controller.py) no tiene ni una línea de SQL; [api_facturas/repositorios/persona/](../api_facturas/repositorios/persona/) no sabe nada de HTTP.

**Contraejemplo (lo que S evita):** meter el SQL dentro del controller. Funcionaría… hasta que toque cambiar de motor y haya que editar 12 controllers.

## O — Open/Closed (Abierto/Cerrado)

> *Abierto para EXTENDER, cerrado para MODIFICAR: lo nuevo se agrega con código nuevo, no editando el viejo.*

**Aplicado:** soportar un motor de BD nuevo (digamos Oracle) NO requiere tocar controllers ni servicios: se escribe un repositorio nuevo (`repositorio_lectura_oracle.py`) y se registra en la fábrica. Todo lo demás queda intacto.

**Véalo:** en `repositorios/` ya conviven tres "extensiones" del mismo concepto: `repositorio_lectura_postgresql.py`, `repositorio_lectura_mysql_mariadb.py`, `repositorio_lectura_sqlserver.py`. Ninguno modificó a los otros al nacer.

## L — Liskov Substitution (Sustitución de Liskov)

> *Cualquier implementación de una interfaz debe poder reemplazar a otra sin que el programa se entere.*

**Aplicado:** el servicio trabaja contra "un repositorio" sin saber cuál. El de PostgreSQL, el de MariaDB y el de SQL Server son **intercambiables**: mismos métodos, mismos parámetros, mismo tipo de resultado (filas como diccionarios).

**Véalo funcionando:** cambie el motor y repita la misma petición — la respuesta tiene la misma forma:

```powershell
$env:DB_PROVIDER = "mariadb"; docker compose up -d
# GET http://localhost:8001/api/persona → mismo JSON que con postgres
```

Si el repositorio de MariaDB retornara los datos "a su manera", violaría Liskov y el servicio tendría que llenarse de `if motor == ...` — justo lo que este diseño evita.

## I — Interface Segregation (Segregación de Interfaces)

> *Mejor varias interfaces pequeñas y específicas que una gigante que obligue a implementar cosas que no se usan.*

**Aplicado:** en `servicios/abstracciones/` y `repositorios/abstracciones/` hay contratos separados y pequeños:

- `i_proveedor_conexion.py` → solo sabe entregar la cadena de conexión
- `i_servicio_crud.py` → solo las operaciones CRUD
- `i_repositorio_lectura_tabla.py` → solo lectura de tablas

Quien implementa uno no está obligado a implementar los demás.

## D — Dependency Inversion (Inversión de Dependencias)

> *Las capas de alto nivel no dependen de clases concretas, sino de abstracciones. Alguien "inyecta" la implementación concreta.*

**Aplicado:** el servicio NO hace `RepositorioPostgreSQL()` por su cuenta. Le pide el repositorio a la **fábrica**, que decide la clase concreta mirando `DB_PROVIDER`:

```
ServicioCrud ──depende de──► IRepositorio (abstracción)
                                   ▲
        FabricaRepositorios ──crea─┴── RepositorioPostgreSQL
        (única que conoce            RepositorioMariaDB
         las clases concretas)       RepositorioSqlServer
```

**Véalo:** `servicios/fabrica_repositorios.py` en cualquiera de las dos APIs. Es también el patrón **Factory** del que habla [ARQUITECTURA_3_CAPAS.md](ARQUITECTURA_3_CAPAS.md).

## SOLID en una frase

Gracias a S-O-L-I-D, este proyecto puede: cambiar de motor con una variable de entorno (L, D), agregar motores sin tocar lo existente (O), y dejar que un compañero trabaje en el front mientras otro toca los repositorios sin pisarse (S, I).

---

# Parte 2 — ACID (transacciones de base de datos)

Una **transacción** es un grupo de operaciones que la BD trata como una sola. ACID son las 4 garantías que la hacen confiable. La BD `bdfacturas` fue diseñada para demostrarlas.

## A — Atomicidad (todo o nada)

> *O se ejecutan TODAS las operaciones de la transacción, o NINGUNA.*

**Aplicado:** el procedimiento almacenado `sp_insertar_factura_y_productosporfactura` (véalo en [db/mariadb/init.sql](../db/mariadb/init.sql)) hace varias cosas: inserta la factura, inserta cada renglón del detalle, descuenta stock y actualiza el total. Si a mitad de camino un producto no tiene stock suficiente, el trigger lanza un error (`SIGNAL`) y **todo se revierte**: no queda una factura a medias, ni stock descontado de más.

**Sin atomicidad pasaría esto:** factura creada ✓, primer producto descontado ✓, segundo producto falla ✗ → la BD queda inconsistente y nadie sabe qué se cobró.

## C — Consistencia (las reglas siempre se cumplen)

> *La transacción lleva la BD de un estado válido a otro estado válido. Las reglas se cumplen SIEMPRE.*

**Aplicado con tres mecanismos** (véalos en cualquier script de `db/`):

1. **Llaves foráneas:** no se puede eliminar una persona que es cliente o vendedor. Pruébelo en el front (Personas → eliminar a Ana Torres) y verá el error de integridad referencial.
2. **Triggers:** `total` de la factura es SIEMPRE la suma de los subtotales, y el subtotal SIEMPRE es cantidad × precio — lo garantiza la BD, no la aplicación.
3. **Validación de stock:** el trigger impide vender más unidades de las que hay.

**Concepto clave del curso:** estas reglas viven en la BD (no solo en Python) porque deben cumplirse **sin importar quién escriba**: la API genérica, la de facturas, phpMyAdmin o un SQL directo.

## I — Aislamiento (transacciones simultáneas no se pisan)

> *Dos transacciones al mismo tiempo se comportan como si fueran una después de la otra.*

**Aplicado:** imagine dos cajeros facturando el último Laptop (stock = 1) en el mismo instante. Sin aislamiento, ambos leerían "hay 1", ambos venderían, y el stock quedaría en −1. Con aislamiento, el motor pone en fila las dos actualizaciones sobre la misma fila (`UPDATE producto SET stock = stock - 1`): la primera gana, la segunda encuentra stock 0 y el trigger la rechaza.

**Detalle de paradigmas:** cada motor lo implementa distinto (bloqueos de fila, versiones de fila/MVCC) y con niveles configurables (`READ COMMITTED`, `REPEATABLE READ`, `SERIALIZABLE`) — buen tema para profundizar comparando PostgreSQL vs SQL Server.

## D — Durabilidad (lo confirmado no se pierde)

> *Cuando la BD dice "listo" (COMMIT), el dato sobrevive a un apagón o reinicio.*

**Aplicado — pruébelo usted mismo:**

```powershell
# 1. Cree un producto en el front (http://localhost:8000/productos)
# 2. Apague TODO:
docker compose down
# 3. Vuelva a encender:
docker compose up -d
# 4. El producto sigue ahí.
```

Dos niveles de durabilidad trabajando juntos: el motor escribe cada COMMIT a su **log de transacciones** en disco, y Docker guarda ese disco en un **volumen** que sobrevive a los contenedores (por eso `down -v` — que borra los volúmenes — sí destruye los datos).

---

## Resumen: dónde ver cada principio

| Principio | Archivo donde verlo |
|---|---|
| **S** — una responsabilidad | `controllers/` vs `servicios/` vs `repositorios/` en ambas APIs |
| **O** — extender sin modificar | los 3 `repositorio_lectura_*.py` conviviendo en `repositorios/` |
| **L** — implementaciones intercambiables | cambiar `DB_PROVIDER` y obtener el mismo JSON |
| **I** — interfaces pequeñas | `servicios/abstracciones/` y `repositorios/abstracciones/` |
| **D** — depender de abstracciones | `servicios/fabrica_repositorios.py` |
| **A** — todo o nada | `sp_insertar_factura_y_productosporfactura` en `db/` |
| **C** — reglas siempre válidas | llaves foráneas y triggers en `db/` |
| **I** — transacciones simultáneas | triggers de stock (`UPDATE ... stock = stock - cantidad`) |
| **D** — lo confirmado permanece | volúmenes en `docker-compose.yml` + log del motor |

## Ejercicios sugeridos

1. **(S/O)** Agregue a la API de facturas un endpoint `GET /api/producto/agotados` (stock = 0). ¿Qué archivos tocó? ¿Cuáles NO tuvo que tocar?
2. **(C)** Desde phpMyAdmin intente `DELETE FROM persona WHERE codigo = 'P001'`. Explique el error con sus palabras.
3. **(A)** Desde el Swagger de la API genérica intente crear un `productosporfactura` con cantidad mayor al stock. ¿Qué pasó con la factura y con el stock?
4. **(D de SOLID)** Encuentre en `fabrica_repositorios.py` la línea exacta donde se decide qué repositorio crear.
5. **(D de ACID)** Ejecute la prueba de durabilidad de arriba, y luego repítala con `down -v`. Explique la diferencia.
