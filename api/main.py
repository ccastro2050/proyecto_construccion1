"""API de ejemplo del Proyecto Paradigmas.

La misma API funciona contra PostgreSQL, MariaDB y SQL Server:
el motor se elige en la ruta, p. ej. /api/postgres/productos.

Documentacion interactiva: http://localhost:8000/docs
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from api.db import MOTORES, get_engine

app = FastAPI(
    title="Proyecto Paradigmas",
    description="API de ejemplo contra PostgreSQL, MariaDB y SQL Server (bdfacturas)",
    version="1.0.0",
)


# ------------------------- Modelos -------------------------

class Producto(BaseModel):
    codigo: str
    nombre: str
    stock: int
    valorunitario: float


class ConsultaSQL(BaseModel):
    sql: str


# ------------------------- Utilidades -------------------------

def _validar_motor(motor: str) -> None:
    if motor not in MOTORES:
        raise HTTPException(
            status_code=404,
            detail=f"Motor '{motor}' no existe. Use: {', '.join(MOTORES)}",
        )


def _filas_a_dicts(resultado) -> list[dict]:
    return [dict(fila._mapping) for fila in resultado]


# ------------------------- Endpoints -------------------------

@app.get("/api/salud")
def salud():
    """Verifica la conexion a los tres motores."""
    estado = {}
    for motor in MOTORES:
        try:
            with get_engine(motor).connect() as con:
                con.execute(text("SELECT 1"))
            estado[motor] = "ok"
        except SQLAlchemyError as e:
            estado[motor] = f"error: {str(e.__cause__ or e)[:200]}"
    return estado


@app.get("/api/{motor}/tablas")
def listar_tablas(motor: str):
    """Lista las tablas de la base de datos del motor indicado."""
    _validar_motor(motor)
    return {"motor": motor, "tablas": inspect(get_engine(motor)).get_table_names()}


@app.get("/api/{motor}/productos")
def listar_productos(motor: str):
    """SELECT basico: todos los productos."""
    _validar_motor(motor)
    with get_engine(motor).connect() as con:
        resultado = con.execute(text("SELECT codigo, nombre, stock, valorunitario FROM producto ORDER BY codigo"))
        return _filas_a_dicts(resultado)


@app.post("/api/{motor}/productos", status_code=201)
def crear_producto(motor: str, p: Producto):
    """INSERT con parametros (evita inyeccion SQL)."""
    _validar_motor(motor)
    try:
        with get_engine(motor).begin() as con:
            con.execute(
                text("INSERT INTO producto (codigo, nombre, stock, valorunitario) "
                     "VALUES (:codigo, :nombre, :stock, :valorunitario)"),
                p.model_dump(),
            )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e.__cause__ or e))
    return {"mensaje": "Producto creado", "producto": p}


@app.put("/api/{motor}/productos/{codigo}")
def actualizar_producto(motor: str, codigo: str, p: Producto):
    """UPDATE con parametros."""
    _validar_motor(motor)
    try:
        with get_engine(motor).begin() as con:
            r = con.execute(
                text("UPDATE producto SET nombre = :nombre, stock = :stock, "
                     "valorunitario = :valorunitario WHERE codigo = :codigo"),
                {**p.model_dump(), "codigo": codigo},
            )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e.__cause__ or e))
    if r.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"Producto {codigo} no existe")
    return {"mensaje": "Producto actualizado", "codigo": codigo}


@app.delete("/api/{motor}/productos/{codigo}")
def borrar_producto(motor: str, codigo: str):
    """DELETE con parametros."""
    _validar_motor(motor)
    try:
        with get_engine(motor).begin() as con:
            r = con.execute(text("DELETE FROM producto WHERE codigo = :codigo"), {"codigo": codigo})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e.__cause__ or e))
    if r.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"Producto {codigo} no existe")
    return {"mensaje": "Producto eliminado", "codigo": codigo}


@app.get("/api/{motor}/facturas")
def listar_facturas(motor: str):
    """JOIN de varias tablas: facturas con cliente y vendedor."""
    _validar_motor(motor)
    sql = text("""
        SELECT f.numero, f.fecha, f.total,
               pc.nombre AS cliente, pv.nombre AS vendedor
        FROM factura f
        JOIN cliente c  ON c.id = f.fkidcliente
        JOIN persona pc ON pc.codigo = c.fkcodpersona
        JOIN vendedor v ON v.id = f.fkidvendedor
        JOIN persona pv ON pv.codigo = v.fkcodpersona
        ORDER BY f.numero
    """)
    with get_engine(motor).connect() as con:
        return _filas_a_dicts(con.execute(sql))


@app.post("/api/{motor}/sql")
def ejecutar_sql(motor: str, consulta: ConsultaSQL):
    """Ejecuta SQL libre contra el motor indicado (solo para practicas).

    Si la sentencia retorna filas (SELECT) se devuelven como JSON;
    si no (INSERT/UPDATE/DELETE/DDL), se devuelve el numero de filas afectadas.
    """
    _validar_motor(motor)
    try:
        with get_engine(motor).begin() as con:
            resultado = con.execute(text(consulta.sql))
            if resultado.returns_rows:
                return {"filas": _filas_a_dicts(resultado)}
            return {"filas_afectadas": resultado.rowcount}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e.__cause__ or e))


# El front estatico se monta al final para no tapar las rutas /api
app.mount("/", StaticFiles(directory="front", html=True), name="front")
