# Proyecto Construcción 1

Proyecto del curso **Construcción de Software 1** (USB Medellín). Entorno de aprendizaje **todo-en-uno con Docker**: una arquitectura real de **3 capas** — frontend Flask, dos APIs FastAPI y tres motores de base de datos — que se levanta completa con **un solo comando**. Solo se necesita Docker Desktop.

> **Para quién es esto:** estudiantes que ya cursaron *Paradigmas de Programación* y *Diseño de Software*. Aquí el foco es la **construcción**: partir de especificaciones (los **spec kits** de abajo, al estilo SDD/GitHub Spec Kit), implementar por capas con SOLID, verificar contra criterios de aceptación y desplegar con Docker. El análisis y el diseño ya vienen documentados en cada README — su trabajo es construir sobre ellos.

```
Navegador → FRONT Flask (8000)
                ├── API GENÉRICA  (8001)  CRUD sobre cualquier tabla
                └── API FACTURAS  (8002)  CRUD por entidad + validación Pydantic
                        └── PostgreSQL · MariaDB · SQL Server  (bdfacturas)
```

> 📖 **Documentación:** [Guía del estudiante](docs/GUIA_ESTUDIANTE.md) · [Arquitectura de 3 capas](docs/ARQUITECTURA_3_CAPAS.md) · [Principios SOLID y ACID aplicados](docs/PRINCIPIOS_SOLID_ACID.md) · [Conceptos clave](docs/CONCEPTOS.md) · [Cómo se construyó el entorno](docs/TUTORIAL_CONSTRUCCION.md) · [SDD y Spec Kit](docs/SDD_SPECKIT.md)
>
> 📐 **Spec kits** (especificación + plan + tareas para reconstruir cada pieza desde cero):
> [Proyecto e infraestructura](docs/spec_kit/2_spec.md) (con la [constitución](docs/spec_kit/1_constitution.md)) ·
> [API Genérica](api_generica/docs/spec_kit/2_spec.md) ·
> [API Facturas](api_facturas/docs/spec_kit/2_spec.md) ·
> [Front Flask](front_flask/docs/spec_kit/2_spec.md)

---

## Puesta en marcha (un solo comando)

En la terminal de VS Code:

```bash
git clone https://github.com/ccastro2050/proyecto_construccion1.git
cd proyecto_construccion1
docker compose up -d --build
```

**Eso es todo.** La primera vez tarda unos minutos (descarga las imágenes). Al terminar:

| Qué | Dónde |
|---|---|
| **Frontend** (Flask + Bootstrap) | http://localhost:8000 |
| **API Genérica** — Swagger | http://localhost:8001/swagger |
| **API Facturas** — Swagger | http://localhost:8002/docs |
| **phpMyAdmin** (admin web de MariaDB) | http://localhost:8081 |
| PostgreSQL 16 · MariaDB 11 · SQL Server 2022 | con la BD `bdfacturas` cargada |

Todo el código está **comentado en español** para quien está comenzando a programar. El código se recarga solo al guardar cambios (front y APIs).

---

## Estructura del proyecto

```
proyecto_construccion1/
├── docker-compose.yml      # Toda la infraestructura declarada aquí
├── db/                     # Scripts de bdfacturas para los 3 motores
│
├── front_flask/            # CAPA 1 — Frontend (puerto 8000)
│   ├── rutas/              #   Blueprints: productos, personas, facturas, explorador
│   ├── servicios/          #   cliente_api.py: consume cualquiera de las 2 APIs
│   └── templates/          #   HTML con Bootstrap 5 (herencia Jinja2)
│
├── api_generica/           # CAPA 2a — API CRUD genérica (puerto 8001)
│   ├── controllers/        #   /api/{tabla} sirve para CUALQUIER tabla
│   ├── servicios/          #   ServicioCrud + Fábrica + BCrypt
│   └── repositorios/       #   PostgreSQL | MariaDB | SQL Server
│
├── api_facturas/           # CAPA 2b — API por entidad (puerto 8002)
│   ├── controllers/        #   Un controller por tabla (12 entidades)
│   ├── models/             #   Modelos Pydantic (validación estricta)
│   ├── servicios/          #   Lógica de negocio por entidad
│   └── repositorios/       #   Un repositorio por entidad y por motor
│
└── docs/                   # Guías y tutoriales
```

Las dos APIs siguen la misma arquitectura interna de sus repos originales:
[ApiGenericaFastApi_Crud](https://github.com/ccastro2050/ApiGenericaFastApi_Crud) y
[ApiFacturasFastApi_Crud](https://github.com/ccastro2050/ApiFacturasFastApi_Crud).

---

## Análisis

### Casos de uso más representativos

```mermaid
flowchart LR
    U(["👤 Usuario web<br/>(estudiante)"])
    A(["🛠️ Administrador<br/>de datos"])

    subgraph SISTEMA["Sistema Proyecto Construcción 1"]
        CU1(["CU-01 Gestionar productos<br/>(CRUD completo)"])
        CU2(["CU-02 Gestionar personas<br/>(CRUD completo)"])
        CU3(["CU-03 Consultar facturas<br/>y su detalle"])
        CU4(["CU-04 Explorar las 12 tablas"])
        CU5(["CU-05 Cambiar la API activa<br/>(Genérica ↔ Facturas)"])
        CU6(["CU-06 Cambiar el motor de BD<br/>(DB_PROVIDER)"])
        CU7(["CU-07 Administrar la BD<br/>(phpMyAdmin / SQLTools)"])
        CU8(["CU-08 Verificar credenciales<br/>(BCrypt)"])
    end

    U --> CU1 & CU2 & CU3 & CU4 & CU5
    A --> CU6 & CU7 & CU8
    CU1 -. include: la escritura<br/>viaja por 3 capas .-> CU3
```

| CU | Flujo principal (resumen) | Regla clave |
|---|---|---|
| CU-01/02 | Listar → formulario → POST → flash → volver a la lista (Post→Redirect→Get) | El front nunca toca la BD: todo pasa por una API |
| CU-03 | Lista de facturas → detalle maestro-detalle | Totales y subtotales los calcula el **trigger** de la BD |
| CU-05 | Dropdown del navbar guarda `session["api"]` | Las pantallas funcionan idéntico con las dos APIs |
| CU-06 | `$env:DB_PROVIDER=...` + `docker compose up -d` | Cero cambios de código: es el punto del curso |

### Historias de usuario

| # | Historia | Criterios de aceptación |
|---|---|---|
| HU-01 | **Como** estudiante **quiero** crear, editar y eliminar productos desde el navegador **para** ver un CRUD real atravesando 3 capas | Flash verde por acción; el cambio se ve en la BD con un cliente SQL |
| HU-02 | **Como** estudiante **quiero** cambiar la API activa sin reiniciar nada **para** comprobar que el front no depende del backend | Mismo comportamiento en todas las pantallas con ambas APIs |
| HU-03 | **Como** estudiante **quiero** cambiar de motor de BD con una variable **para** entender la inversión de dependencias | `postgres`/`mariadb`/`sqlserver` producen resultados idénticos |
| HU-04 | **Como** estudiante **quiero** ver el error de llave foránea al eliminar una persona usada como cliente **para** entender integridad referencial | La alerta roja muestra el mensaje textual del motor |
| HU-05 | **Como** profesor **quiero** que todo arranque con un comando **para** no perder clase instalando software | `docker compose up -d --build` deja los 8 servicios listos |
| HU-06 | **Como** estudiante **quiero** que mis datos sobrevivan al apagado **para** retomar la clase siguiente | `down` + `up -d` conserva datos; solo `down -v` los borra |

---

## Diseño

### Arquitectura (vista de contenedores)

```mermaid
flowchart TB
    NAV["🌐 Navegador"]

    subgraph CAPA1["CAPA 1 — Presentación"]
        FRONT["front (Flask + Jinja2 + Bootstrap)<br/>:8000 · sin drivers de BD"]
    end

    subgraph CAPA2["CAPA 2 — Lógica / APIs"]
        AG["api-generica (FastAPI)<br/>:8001 · /api/{tabla} para CUALQUIER tabla"]
        AF["api-facturas (FastAPI)<br/>:8002 · 1 CRUD por entidad + Pydantic"]
    end

    subgraph CAPA3["CAPA 3 — Datos (elegible con DB_PROVIDER)"]
        PG[("PostgreSQL 16<br/>:15432")]
        MA[("MariaDB 11<br/>:13306")]
        MS[("SQL Server 2022<br/>:11433")]
    end

    NAV -->|HTTP| FRONT
    FRONT -->|"HTTP (según API activa en sesión)"| AG
    FRONT -->|HTTP| AF
    AG -->|SQL parametrizado| PG & MA & MS
    AF -->|SQL parametrizado| PG & MA & MS
    PG -.->|"trigger + SPs<br/>(totales, stock, RBAC)"| PG
```

**Regla de dependencias:** cada capa solo conoce a la inmediatamente inferior, y siempre a través de un contrato (HTTP entre front y APIs; interfaces `Protocol` + fábrica entre APIs y motores).

### Diseño de base de datos (bdfacturas — idéntica en los 3 motores)

```mermaid
erDiagram
    persona ||--o{ cliente : "es"
    persona ||--o{ vendedor : "es"
    empresa ||--o{ cliente : "respalda"
    cliente ||--o{ factura : "compra"
    vendedor ||--o{ factura : "vende"
    factura ||--|{ productosporfactura : "detalla"
    producto ||--o{ productosporfactura : "aparece en"
    usuario ||--o{ rol_usuario : "tiene"
    rol ||--o{ rol_usuario : "asignado a"
    ruta ||--o{ rutarol : "protegida por"
    rol ||--o{ rutarol : "accede a"

    persona { varchar codigo PK
              varchar nombre
              varchar email
              varchar telefono }
    empresa { varchar codigo PK
              varchar nombre }
    producto { varchar codigo PK
               varchar nombre
               int stock
               numeric valorunitario }
    cliente { int id PK
              numeric credito
              varchar fkcodpersona FK
              varchar fkcodempresa FK }
    vendedor { int id PK
               int carnet
               varchar direccion
               varchar fkcodpersona FK }
    factura { int numero PK
              timestamp fecha
              numeric total
              varchar estado
              int fkidcliente FK
              int fkidvendedor FK }
    productosporfactura { int fknumfactura PK,FK
                          varchar fkcodproducto PK,FK
                          int cantidad
                          numeric subtotal }
    usuario { varchar email PK
              varchar contrasena }
    rol { int id PK
          varchar nombre }
    rol_usuario { varchar fkemail PK,FK
                  int fkidrol PK,FK }
    ruta { int id PK
           varchar ruta UK
           varchar descripcion }
    rutarol { int fkidruta PK,FK
              int fkidrol PK,FK }
```

Decisiones de diseño de datos: PK compuestas en las 3 tablas puente; `ON DELETE CASCADE` de factura→detalle y en rutarol; la **lógica de negocio vive en la BD** — el trigger `actualizar_totales_y_stock` valida stock, calcula `subtotal = cantidad × valorunitario`, descuenta stock y recalcula `total` en cada INSERT/UPDATE/DELETE del detalle; ~15 procedimientos almacenados (facturación, usuarios con roles, RBAC) devuelven JSON.

### Diseño de interfaz (front)

```mermaid
flowchart LR
    INICIO["🏠 Inicio<br/>estado de las 2 APIs"]
    PROD["📦 Productos<br/>lista"]
    PFORM["Formulario<br/>crear/editar"]
    PERS["👥 Personas<br/>lista"]
    PEFORM["Formulario<br/>crear/editar"]
    FACT["🧾 Facturas<br/>lista (solo lectura)"]
    FDET["Detalle<br/>maestro-detalle"]
    EXPL["🗂️ Explorador<br/>12 tablas"]

    INICIO --> PROD & PERS & FACT & EXPL
    PROD <--> PFORM
    PERS <--> PEFORM
    FACT --> FDET
```

Patrones de UI fijos: navbar oscuro con selector de API (dropdown, opción activa marcada) · mensajes **flash** `success`/`danger` como alertas Bootstrap descartables · eliminar siempre por POST con `confirm()` · formulario compartido crear/editar con la PK deshabilitada al editar · degradación elegante (API caída = alerta + página vacía navegable). Las APIs exponen su propia "interfaz": Swagger en `:8001/swagger` y `:8002/docs`.

### Diagramas de secuencia más representativos

**1. Crear un producto — la escritura atraviesa las 3 capas:**

```mermaid
sequenceDiagram
    actor U as Usuario
    participant F as front (Flask)
    participant C as ClienteApi
    participant A as API activa (8001/8002)
    participant S as Servicio
    participant R as Repositorio(Motor)
    participant BD as BD (DB_PROVIDER)

    U->>F: POST /productos/nuevo (form)
    F->>C: crear("producto", {codigo, nombre, stock, valorunitario})
    C->>A: POST /api/producto  (JSON, timeout 10s)
    A->>S: fábrica crea servicio según DB_PROVIDER
    S->>R: crear(datos)  — valida no-vacíos
    R->>BD: INSERT ... VALUES (:codigo, :nombre, ...) parametrizado
    BD-->>R: rowcount = 1
    R-->>A: True
    A-->>C: 200 {estado, mensaje}
    C-->>F: (True, "Registro creado correctamente.")
    F-->>U: redirect a /productos/ + flash verde (Post→Redirect→Get)
```

**2. Insertar un renglón de factura — la BD hace el trabajo pesado:**

```mermaid
sequenceDiagram
    participant CL as Cliente HTTP
    participant A as API (cualquiera de las 2)
    participant BD as BD bdfacturas
    participant TG as trigger actualizar_totales_y_stock

    CL->>A: POST /api/productosporfactura {fknumfactura:1, fkcodproducto:"PR003", cantidad:2, subtotal:0}
    A->>BD: INSERT parametrizado (subtotal llega en 0)
    BD->>TG: BEFORE INSERT
    TG->>TG: ¿stock suficiente? (si no → EXCEPTION → API responde 500 con el mensaje)
    TG->>BD: subtotal := cantidad × valorunitario
    TG->>BD: UPDATE producto SET stock = stock - 2
    TG->>BD: UPDATE factura SET total = Σ subtotales
    BD-->>A: OK
    A-->>CL: 200 — la API nunca calculó nada
```

**3. Cambiar la API activa — el front no depende del backend:**

```mermaid
sequenceDiagram
    actor U as Usuario
    participant F as front (Flask)

    U->>F: GET /cambiar-api/facturas (clic en el dropdown)
    F->>F: whitelist: ¿"generica" o "facturas"? ✓
    F->>F: session["api"] = "facturas" (cookie firmada)
    F-->>U: redirect al referrer
    Note over U,F: Desde ahora ClienteApi arma URLs contra :8002.<br/>Ninguna plantilla ni ruta cambió.
```

### Principios SOLID en el sistema

| Principio | Dónde se ve en este repo |
|---|---|
| **S** — Responsabilidad única | front pinta, APIs deciden, BD persiste; dentro de cada API: controller / servicio / repositorio |
| **O** — Abierto/cerrado | Motor nuevo = 1 repositorio + 1 línea en la fábrica; el resto no se toca |
| **L** — Sustitución de Liskov | Los 3 repositorios de cada operación son intercambiables: cambiar `DB_PROVIDER` no rompe nada |
| **I** — Segregación de interfaces | Protocols pequeños: `IProveedorConexion` (2 miembros), `IRepositorio*` (solo sus operaciones) |
| **D** — Inversión de dependencias | Servicios reciben **interfaces** por constructor; solo la fábrica conoce clases concretas |

> Detalle con ejercicios: [docs/PRINCIPIOS_SOLID_ACID.md](docs/PRINCIPIOS_SOLID_ACID.md). Diseño completo por componente: los spec kits enlazados arriba.

---

## Despliegue

Todo el sistema se despliega como **8 contenedores + 3 volúmenes** en un solo host con Docker Compose:

```mermaid
flowchart TB
    subgraph HOST["💻 PC del estudiante (Docker Desktop)"]
        subgraph NET["red interna de compose"]
            F["front<br/>python:3.12-slim"]
            G["api-generica<br/>python:3.12-slim + msodbcsql18"]
            FA["api-facturas<br/>python:3.12-slim + msodbcsql18"]
            P[("postgres:16-alpine")]
            M[("mariadb:11")]
            S[("mssql/server:2022")]
            INIT["sqlserver-init<br/>(efímero: crea la BD y muere)"]
            PMA["phpmyadmin"]
        end
        V1[/"volumen pgdata"/]
        V2[/"volumen mariadbdata"/]
        V3[/"volumen mssqldata"/]
    end

    B["🌐 Navegador"] -->|8000| F
    B -->|8001 /swagger| G
    B -->|8002 /docs| FA
    B -->|8081| PMA
    HERR["🛠️ pgAdmin · HeidiSQL · SSMS"] -->|15432 / 13306 / 11433| P & M & S

    F --> G & FA
    G & FA --> P & M & S
    INIT -.->|"espera healthcheck<br/>y ejecuta bdfacturas.sql"| S
    PMA --> M
    P --- V1
    M --- V2
    S --- V3
```

| Aspecto | Decisión |
|---|---|
| Orquestación | `docker-compose.yml` único; `restart: unless-stopped` en apps |
| Inicialización de BD | Postgres/MariaDB: `init.sql` en `/docker-entrypoint-initdb.d` (solo con volumen vacío); SQL Server: contenedor auxiliar `sqlserver-init` |
| Desarrollo | Código montado como volumen + `--debug`/`--reload` → guardar recarga sin rebuild |
| Persistencia | Volúmenes nombrados; `down -v` = reset a datos originales |
| Salud | Healthchecks por motor (`pg_isready`, `healthcheck.sh`, `sqlcmd SELECT 1`) |
| Entornos | El mismo compose sirve para clase y casa; no existe (a propósito) despliegue a producción |

---

## Cambiar el motor de base de datos

Las dos APIs usan el motor que diga `DB_PROVIDER` (por defecto `postgres`):

```powershell
$env:DB_PROVIDER = "mariadb";   docker compose up -d    # MariaDB
$env:DB_PROVIDER = "sqlserver"; docker compose up -d    # SQL Server
$env:DB_PROVIDER = "postgres";  docker compose up -d    # PostgreSQL (defecto)
```

El front y el resto del sistema no cambian en nada — ese es el punto del curso.

---

## Administrar las bases de datos

- **phpMyAdmin** (MariaDB, sin instalar nada): http://localhost:8081
- **SQLTools en VS Code** (los 3 motores): `F1` → *Dev Containers: Reopen in Container* → icono del cilindro
- **Herramientas locales**: pgAdmin (`localhost:15432`), HeidiSQL (`localhost:13306`), SSMS (`localhost,11433`)

| Motor | Base de datos | Usuario | Contraseña | Puerto en su PC |
|---|---|---|---|---|
| PostgreSQL | `bdfacturas_postgres_local` | `paradigmas` | `paradigmas123` | `15432` |
| MariaDB | `bdfacturas_mariadb_local` | `paradigmas` | `paradigmas123` | `13306` |
| SQL Server | `bdfacturas_sqlserver_local` | `sa` | `Paradigmas123!` | `11433` |

---

## Comandos útiles

```bash
docker compose down          # apagar todo (los datos se conservan)
docker compose up -d         # volver a encender (segundos)
docker compose down -v       # resetear las BD a su estado original
docker compose ps            # estado de los contenedores
docker compose logs front    # errores del front (o api-generica / api-facturas)
```

---

*Proyecto Construcción 1 · USB Med · Base de datos bdfacturas (facturación + RBAC con triggers y stored procedures)*
