"""
rutas/personas.py — CRUD completo de personas.

Sigue EXACTAMENTE el mismo patrón que rutas/productos.py.
Compárelos lado a lado: solo cambian la tabla, los campos
del formulario y las plantillas. Ese es el ejercicio:
entender el patrón para poder repetirlo con cualquier tabla.
"""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from servicios.cliente_api import ClienteApi

bp_personas = Blueprint("personas", __name__, url_prefix="/personas")

TABLA = "persona"
CLAVE = "codigo"


def _api() -> ClienteApi:
    """Cliente para la API seleccionada por el usuario."""
    return ClienteApi(session.get("api", "generica"))


@bp_personas.route("/")
def listar():
    """READ — lista todas las personas."""
    exito, resultado = _api().listar(TABLA)
    if not exito:
        flash(resultado, "danger")
        resultado = []
    return render_template("personas_lista.html", personas=resultado)


@bp_personas.route("/nuevo", methods=["GET", "POST"])
def crear():
    """CREATE — GET muestra el formulario, POST envía a la API."""
    if request.method == "POST":
        datos = {
            "codigo": request.form["codigo"].strip(),
            "nombre": request.form["nombre"].strip(),
            "email": request.form["email"].strip(),
            "telefono": request.form["telefono"].strip(),
        }
        exito, mensaje = _api().crear(TABLA, datos)
        flash(mensaje, "success" if exito else "danger")
        if exito:
            return redirect(url_for("personas.listar"))

    return render_template("personas_formulario.html", persona=None)


@bp_personas.route("/editar/<codigo>", methods=["GET", "POST"])
def editar(codigo: str):
    """UPDATE — GET pre-llena el formulario, POST guarda los cambios."""
    api = _api()

    if request.method == "POST":
        datos = {
            "codigo": codigo,
            "nombre": request.form["nombre"].strip(),
            "email": request.form["email"].strip(),
            "telefono": request.form["telefono"].strip(),
        }
        exito, mensaje = api.actualizar(TABLA, CLAVE, codigo, datos)
        flash(mensaje, "success" if exito else "danger")
        if exito:
            return redirect(url_for("personas.listar"))

    exito, persona = api.obtener(TABLA, CLAVE, codigo)
    if not exito:
        flash(persona, "danger")
        return redirect(url_for("personas.listar"))
    return render_template("personas_formulario.html", persona=persona)


@bp_personas.route("/eliminar/<codigo>", methods=["POST"])
def eliminar(codigo: str):
    """DELETE — elimina por clave primaria (con POST, nunca con GET)."""
    exito, mensaje = _api().eliminar(TABLA, CLAVE, codigo)
    flash(mensaje, "success" if exito else "danger")
    return redirect(url_for("personas.listar"))
