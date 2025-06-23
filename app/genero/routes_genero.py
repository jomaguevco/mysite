from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from .control_genero import obtener_generos, dar_de_baja_genero, obtener_genero_por_id, insertar_genero, ejecutar_consulta, actualizar_genero, buscar_generos_por_nombre, existe_genero, eliminar_genero_sin_productos

from app import csrf
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('genero', __name__, url_prefix='/genero')

@csrf.exempt
@bp.route('/panel_genero_home')
def panel_genero_home():
    try:
        generos = obtener_generos()
    except Exception as e:
        flash(f"Error al cargar los géneros: {e}", "error")
        return render_template('panel/genero.html', generos=[])

    return render_template('panel/genero.html', generos=generos)

@csrf.exempt
@bp.route("/agregar")
def formulario_agregar_genero():
    return render_template("panel/agregar_genero.html")

@csrf.exempt





@bp.route("/dar_de_baja_genero/<int:id_genero>", methods=["POST"])
def dar_de_baja_genero_view(id_genero):
    try:
        # Obtener el género por ID
        genero = obtener_genero_por_id(id_genero)

        # Validar si el género existe
        if not genero:
            flash("El género no existe.", "error")
            return redirect(url_for('genero.panel_genero_home'))

        # Validar si ya está dado de baja
        if genero[2] == 'I':  # Supongo que genero[2] es el estado ('I' = Inactivo)
            flash(f"El género '{genero[1]}' ya fue dado de baja anteriormente.", "error")
            return redirect(url_for('genero.panel_genero_home'))

        # Dar de baja al género
        dar_de_baja_genero(id_genero)
        flash(f"Género '{genero[1]}' dado de baja correctamente.", "success")
    except Exception as e:
        flash(f"Error al dar de baja el género: {e}", "error")

    return redirect(url_for('genero.panel_genero_home'))


@csrf.exempt
@bp.route("/editar/<int:id_genero>")
def editar_genero_view(id_genero):
    try:
        genero = obtener_genero_por_id(id_genero)  # Obtener el género a partir del ID
    except Exception as e:
        flash(f"Error al obtener los datos del género: {e}", "error")
        return redirect(url_for('genero.panel_genero_home'))

    if not genero:
        flash("Género no encontrado.", "error")
        return redirect(url_for('genero.panel_genero_home'))

    return render_template("panel/editar_genero.html", genero=genero)

@csrf.exempt
@bp.route("/guardar", methods=["POST"])
def guardar_genero():
    nombre_genero = request.form["nombre_genero"]
    estado_genero = request.form["estado_genero"]

    if not nombre_genero or not estado_genero:
        flash("Todos los campos son obligatorios.", "error_guardar_genero")
        return redirect(url_for('genero.formulario_agregar_genero'))

    genero_existente = existe_genero(nombre_genero)
    if genero_existente:
        flash(f"El género '{nombre_genero}' ya existe.", "error_guardar_genero")
        return redirect(url_for('genero.formulario_agregar_genero'))

    try:
        insertar_genero(nombre_genero, estado_genero)
        flash(f"Género '{nombre_genero}' agregado con éxito.", "success_guardar_genero")
    except Exception as e:
        flash(f"Error al guardar el género: {e}", "error_guardar_genero")

    return redirect(url_for('genero.panel_genero_home'))

@csrf.exempt
@bp.route("/actualizar/<int:id_genero>", methods=["POST"])
def actualizar_genero_view(id_genero):
    nombre_genero = request.form.get("nombre_genero")
    estado_genero = request.form.get("estado_genero")

    if not nombre_genero or not estado_genero:
        flash("Todos los campos son obligatorios.", "error_actualizar_genero")
        return redirect(url_for('genero.editar_genero_view', id_genero=id_genero))

    try:
        genero_existente = existe_genero(nombre_genero)

        if genero_existente and genero_existente[0] != id_genero:
            flash(f"El género '{nombre_genero}' ya existe.", "error_actualizar_genero")
            return redirect(url_for('genero.editar_genero_view', id_genero=id_genero))

        actualizar_genero(id_genero, nombre_genero, estado_genero)
        flash(f"Género actualizado correctamente.", "success_actualizar_genero")
    except Exception as e:
        flash(f"Error al actualizar el género: {e}", "error_actualizar_genero")

    return redirect(url_for('genero.panel_genero_home'))

@csrf.exempt
@bp.route("/eliminar/<int:id_genero>", methods=["POST"])
def eliminar_genero(id_genero):
    try:
        genero = obtener_genero_por_id(id_genero)
        nombre_genero = genero[1]

        eliminado = eliminar_genero_sin_productos(id_genero)
        if eliminado:
            flash(f"Género '{nombre_genero}' eliminado con éxito.", "success")
        else:
            flash(f"No se puede eliminar el género '{nombre_genero}' porque está asociado a productos.", "error")
    except Exception as e:
        flash(f"Error al intentar eliminar el género: {e}", "error")

    return redirect(url_for('genero.panel_genero_home'))

@csrf.exempt
@bp.route('/buscar', methods=['GET'])
def buscar_genero():
    nombre_genero = request.args.get("nombre_genero", "").strip()

    if not nombre_genero:
        flash("Debes ingresar un nombre para buscar.", "error")
        return redirect(url_for('genero.panel_genero_home'))

    try:
        generos = buscar_generos_por_nombre(nombre_genero)
        if not generos:
            return render_template('panel/genero.html', generos=[])

        return render_template('panel/genero.html', generos=generos)
    except Exception as e:
        flash(f"Error al buscar géneros: {e}", "error")
        return redirect(url_for('genero.panel_genero_home'))

@csrf.exempt
@bp.route("/filtrar_genero", methods=["GET"])
def filtrar_genero():
    filtro_orden = request.args.get("filtro_orden", "todos")

    consulta = "SELECT * FROM GENERO"

    if filtro_orden == "A":
        consulta += " WHERE ESTADO_GENERO = 'A'"
    elif filtro_orden == "I":
        consulta += " WHERE ESTADO_GENERO = 'I'"

    if filtro_orden == "asc":
        consulta += " ORDER BY NOMBRE_GENERO ASC"
    elif filtro_orden == "desc":
        consulta += " ORDER BY NOMBRE_GENERO DESC"

    generos = ejecutar_consulta(consulta)
    return render_template('panel/genero.html', generos=generos)


#apis
@csrf.exempt
@bp.route("/APIobtener_todos", methods=["GET"])
@jwt_required()
def api_obtener_todos():
    rpta = dict()
    try:
        generos = obtener_generos()
        rpta["data"] = generos
        rpta["message"] = "Listado de géneros obtenido correctamente"
        rpta["status"] = 1
        return jsonify(rpta), 200

    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un error: {repr(e)}"
        rpta["status"] = -1
        return jsonify(rpta), 500

@csrf.exempt
@bp.route("/APIinsertar", methods=["POST"])
@jwt_required()
def api_insertar_genero():
    rpta = dict()
    try:
        nombre = request.json.get("nombre_genero")
        estado = request.json.get("estado", "A")
        if not nombre:
            rpta["data"] =  {
            "nombre_genero": nombre,
            "estado": estado
            }
            rpta["message"] = "El nombre del género es obligatorio"
            rpta["status"] = 0
            return jsonify(rpta)
        else:
            insertar_genero(nombre, estado)
            rpta["data"] = {}
            rpta["message"] = "Género registrado correctamente"
            rpta["status"] = 1
            return jsonify(rpta)
    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = "Ocurrió un error inesperado: " + repr(e)
        rpta["status"] = -1
        return jsonify(rpta)


@csrf.exempt
@bp.route("/APIbuscar", methods=["POST"])
@jwt_required()
def api_buscar_generos():
    rpta = dict()
    nombre_genero = request.json.get("nombre_genero")
    if not nombre_genero or not nombre_genero.strip():
        rpta["data"] = {}
        rpta["message"] = "El nombre del género es obligatorio"
        rpta["status"] = 0
        return jsonify(rpta)
    try:
        generos = buscar_generos_por_nombre(nombre_genero)
        if not generos:
            rpta["data"] = {}
            rpta["message"] = "No se encontraron géneros con ese nombre"
            rpta["status"] = 0
        else:
            rpta["data"] = generos
            rpta["message"] = "Búsqueda de géneros realizada correctamente"
            rpta["status"] = 1
        return jsonify(rpta)
    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = "Ocurrió un error: " + repr(e)
        rpta["status"] = -1
        return jsonify(rpta)





@csrf.exempt
@bp.route("/APIdar_de_baja/<int:id_genero>", methods=["POST"])
@jwt_required()
def api_dar_de_baja_genero(id_genero):
    rpta = dict()
    try:
        genero = obtener_genero_por_id(id_genero)
        if not genero:
            rpta["data"] = {}
            rpta["message"] = "Género no encontrado"
            rpta["status"] = 0
            return jsonify(rpta)
        if genero[2] == "I":
            rpta["data"] = genero
            rpta["message"] = "El género ya está inactivo"
            rpta["status"] = 0
            return jsonify(rpta)
        dar_de_baja_genero(id_genero)
        rpta["data"] = {}
        rpta["message"] = "Género dado de baja exitosamente"
        rpta["status"] = 1
        return jsonify(rpta)
    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = "Ocurrió un error inesperado: " + repr(e)
        rpta["status"] = -1
        return jsonify(rpta)

@csrf.exempt
@bp.route("/APIobtener/<int:id_genero>", methods=["GET"])
@jwt_required()
def api_obtener_genero_por_id(id_genero):
    rpta = dict()
    try:
        genero = obtener_genero_por_id(id_genero)
        if not genero:
            rpta["data"] = {}
            rpta["message"] = "Género no encontrado"
            rpta["status"] = 0
            return jsonify(rpta)
        rpta["data"] = genero
        rpta["message"] = "Género obtenido correctamente"
        rpta["status"] = 1
        return jsonify(rpta)
    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = "Ocurrió un error: " + repr(e)
        rpta["status"] = -1
        return jsonify(rpta)

@csrf.exempt
@bp.route("/APIactualizar/<int:id_genero>", methods=["POST"])
@jwt_required()
def api_actualizar_genero(id_genero):
    rpta = dict()
    data = request.get_json()
    nombre_genero = data.get("nombre_genero")
    estado_genero = data.get("estado_genero")
    if not nombre_genero or not estado_genero:
        rpta["data"] = {}
        rpta["message"] = "Todos los campos son obligatorios"
        rpta["status"] = 0
        return jsonify(rpta)
    try:
        genero = obtener_genero_por_id(id_genero)
        if not genero:
            rpta["data"] = {}
            rpta["message"] = "Id del género no encontrado"
            rpta["status"] = 1
        else:
            actualizar_genero(id_genero, nombre_genero, estado_genero)
            rpta["data"] = {}
            rpta["message"] = "Género actualizado exitosamente"
            rpta["status"] = 1
        return jsonify(rpta)
    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = "Ocurrió un error inesperado: " + repr(e)
        rpta["status"] = -1
        return jsonify(rpta)

@csrf.exempt
@bp.route("/APIeliminar", methods=["POST"])
@jwt_required()
def api_eliminar_genero():
    rpta = dict()
    try:
        data = request.get_json()
        id_genero = data.get("id_genero")
        if not id_genero:
            rpta["data"] = {}
            rpta["message"] = "El id del género es obligatorio"
            rpta["status"] = 0
            return jsonify(rpta)

        genero = obtener_genero_por_id(id_genero)

        if not genero:
            rpta["data"] = {}
            rpta["message"] = "No se encontró el género"
            rpta["status"] = 0
            return jsonify(rpta)
        eliminado = eliminar_genero_sin_productos(id_genero)

        if eliminado:
            rpta["data"] = {}
            rpta["message"] = "Género eliminado exitosamente"
            rpta["status"] = 1
            return jsonify(rpta)
        else:
            rpta["data"] = {}
            rpta["message"] = "No se puede eliminar el género porque tiene productos asociados"
            rpta["status"] = 0
            return jsonify(rpta)
    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = "Ocurrió un error inesperado: " + repr(e)
        rpta["status"] = -1
        return jsonify(rpta)


