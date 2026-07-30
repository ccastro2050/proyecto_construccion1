"""
rutas/productos.py — CRUD completo de productos.

Este archivo es EL EJEMPLO GUÍA del proyecto: muestra el ciclo
completo Crear / Leer / Actualizar / Eliminar desde un frontend.
Las rutas de personas siguen exactamente el mismo patrón.

CONCEPTO — Flujo de un formulario web clásico (sin JavaScript):
    GET  /productos/nuevo   → muestra el formulario vacío
    POST /productos/nuevo   → recibe los datos escritos y llama a la API
    (patrón "Post/Redirect/Get": tras guardar, se redirige al listado
     para que refrescar la página no repita el POST)
"""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from servicios.cliente_api import ClienteApi

bp_productos = Blueprint("productos", __name__, url_prefix="/productos")

# La tabla y su clave primaria (la API genérica necesita saber la clave)
TABLA = "producto"
CLAVE = "codigo"


def _api() -> ClienteApi:
    """Crea el cliente para la API que el usuario tenga seleccionada."""
    return ClienteApi(session.get("api", "generica"))


# ================================================================
# READ — Listar
# ================================================================

@bp_productos.route("/")
def listar():
    """Muestra la tabla con todos los productos."""
    exito, resultado = _api().listar(TABLA)
    if not exito:
        # flash() deja un mensaje que la plantilla base muestra como alerta
        flash(resultado, "danger")
        resultado = []
    return render_template("productos_lista.html", productos=resultado)


# ================================================================
# CREATE — Crear
# ================================================================

@bp_productos.route("/nuevo", methods=["GET", "POST"])
def crear():
    """GET: muestra el formulario vacío. POST: envía el producto a la API."""
    if request.method == "POST":
        # request.form trae lo que el usuario escribió en el formulario.
        # Se convierten los números porque los formularios envían todo como texto.
        datos = {
            "codigo": request.form["codigo"].strip(),
            "nombre": request.form["nombre"].strip(),
            "stock": int(request.form["stock"]),
            "valorunitario": float(request.form["valorunitario"]),
        }
        exito, mensaje = _api().crear(TABLA, datos)
        flash(mensaje, "success" if exito else "danger")
        if exito:
            return redirect(url_for("productos.listar"))   # Post → Redirect → Get

    # GET (o POST fallido): mostrar el formulario
    return render_template("productos_formulario.html", producto=None)


# ================================================================
# UPDATE — Editar
# ================================================================

@bp_productos.route("/editar/<codigo>", methods=["GET", "POST"])
def editar(codigo: str):
    """GET: formulario con los datos actuales. POST: guarda los cambios."""
    api = _api()

    if request.method == "POST":
        datos = {
            "codigo": codigo,                    # la clave no se cambia
            "nombre": request.form["nombre"].strip(),
            "stock": int(request.form["stock"]),
            "valorunitario": float(request.form["valorunitario"]),
        }
        exito, mensaje = api.actualizar(TABLA, CLAVE, codigo, datos)
        flash(mensaje, "success" if exito else "danger")
        if exito:
            return redirect(url_for("productos.listar"))

    # GET: buscar el producto para pre-llenar el formulario
    exito, producto = api.obtener(TABLA, CLAVE, codigo)
    if not exito:
        flash(producto, "danger")               # aquí "producto" es el mensaje de error
        return redirect(url_for("productos.listar"))
    return render_template("productos_formulario.html", producto=producto)


# ================================================================
# DELETE — Eliminar
# ================================================================

@bp_productos.route("/eliminar/<codigo>", methods=["POST"])
def eliminar(codigo: str):
    """
    Elimina un producto. Se usa POST (no GET) porque una acción
    destructiva nunca debe dispararse con un simple enlace.
    """
    exito, mensaje = _api().eliminar(TABLA, CLAVE, codigo)
    flash(mensaje, "success" if exito else "danger")
    return redirect(url_for("productos.listar"))
