from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from flask_jwt_extended import jwt_required, get_jwt_identity
from .control_descuento import *
from app import csrf
from datetime import datetime

bp = Blueprint('descuento', __name__, url_prefix='/descuento')

# Mostrar la lista de descuentos
@csrf.exempt
@bp.route('/panel_descuento_home')
def panel_descuento_home():
    try:
        descuentos = obtener_descuentos()
    except Exception as e:
        flash(f"Error al cargar los descuentos: {e}", "error")
        return render_template('panel/descuento.html', descuentos=[])

    return render_template('panel/descuento.html', descuentos=descuentos)

# Formulario para agregar un nuevo descuento
@csrf.exempt
@bp.route("/agregar")
def formulario_agregar_descuento():
    return render_template("panel/agregar_descuento.html")
# Guardar un nuevo descuento
@csrf.exempt
@bp.route("/guardar", methods=["POST"])
def guardar_descuento():
    porcentaje = request.form.get("porcentaje")
    fecha_inicio = request.form.get("fecha_inicio")
    fecha_fin = request.form.get("fecha_fin")
    estado = request.form.get("estado_dscto")

    # Validar que todos los campos sean obligatorios
    if not porcentaje or not fecha_inicio or not estado:
        flash("Todos los campos son obligatorios.", "error_guardar_descuento")
        return redirect(url_for('descuento.formulario_agregar_descuento'))

    # Validar que la fecha de inicio no sea mayor que la fecha de fin
    if fecha_fin and fecha_fin < fecha_inicio:
        flash("La fecha de fin no puede ser anterior a la fecha de inicio.", "error_guardar_descuento")
        return redirect(url_for('descuento.formulario_agregar_descuento'))

    # Insertar el descuento
    try:
        if insertar_descuento(porcentaje, fecha_inicio, fecha_fin, estado):
            flash(f"Descuento del {porcentaje}% agregado con éxito.", "success_guardar_descuento")
        else:
            flash("Error: No se pudo agregar el descuento. Verifique que no exista un descuento igual.", "error_guardar_descuento")
            return redirect(url_for('descuento.formulario_agregar_descuento'))

    except Exception as e:
        flash(f"Error al guardar el descuento: {e}", "error_guardar_descuento")

    return redirect(url_for('descuento.panel_descuento_home'))

@csrf.exempt
@bp.route("/actualizar/<int:id_descuento>", methods=["POST"])
def actualizar_descuento_view(id_descuento):
    porcentaje = request.form.get("porcentaje")
    fecha_inicio = request.form.get("fecha_inicio")
    fecha_fin = request.form.get("fecha_fin")
    estado = request.form.get("estado_dscto")  # Verifica que el nombre del campo en el formulario sea correcto

    # Validar que todos los campos sean obligatorios
    if not porcentaje or not fecha_inicio or not estado:
        flash("Todos los campos son obligatorios.", "error_actualizar_descuento")
        return redirect(url_for('descuento.editar_descuento_view', id_descuento=id_descuento))

    # Validar que la fecha de inicio no sea mayor que la fecha de fin
    if fecha_fin and fecha_fin < fecha_inicio:
        flash("La fecha de fin no puede ser anterior a la fecha de inicio.", "error_actualizar_descuento")
        return redirect(url_for('descuento.editar_descuento_view', id_descuento=id_descuento))

    try:
        if actualizar_descuento(id_descuento, porcentaje, fecha_inicio, fecha_fin, estado):
            flash(f"Descuento actualizado correctamente.", "success_actualizar_descuento")
        else:
            flash(f"Error: No se pudo actualizar el descuento. Verifique que no exista uno igual.", "error_actualizar_descuento")
            return redirect(url_for('descuento.editar_descuento_view', id_descuento=id_descuento))

    except Exception as e:
        flash(f"Error al actualizar el descuento: {e}", "error_actualizar_descuento")

    return redirect(url_for('descuento.panel_descuento_home'))


@csrf.exempt
@bp.route("/editar/<int:id_descuento>")
def editar_descuento_view(id_descuento):
    try:
        descuento = obtener_descuento_por_id(id_descuento)
        if descuento:
            # Formatear las fechas al formato Y-m-d para mostrarlas en el input date
            descuento = list(descuento)  # Convertir a lista si es una tupla
            descuento[2] = descuento[2].strftime('%Y-%m-%d')  # fecha_inicio
            if descuento[3]:  # Verificar si hay fecha_fin
                descuento[3] = descuento[3].strftime('%Y-%m-%d')  # fecha_fin
    except Exception as e:
        flash(f"Error al obtener los datos del descuento: {e}", "error")
        return redirect(url_for('descuento.panel_descuento_home'))

    if not descuento:
        flash("Descuento no encontrado.", "error")
        return redirect(url_for('descuento.panel_descuento_home'))

    return render_template("panel/editar_descuento.html", descuento=descuento)


@csrf.exempt
@bp.route("/dar_de_baja_descuento", methods=["POST"])
def dar_de_baja_descuento_view():
    id_descuento = request.form.get("id_descuento")

    if not id_descuento:
        flash("ID de descuento no proporcionado.", "error")
        return redirect(url_for('descuento.panel_descuento_home'))

    try:
        if dar_de_baja_descuento(id_descuento):
            flash("Descuento dado de baja correctamente.", "success")
        else:
            flash("El descuento ya fue dado de baja anteriormente.", "error")
    except Exception as e:
        flash(f"Error al dar de baja el descuento: {e}", "error")

    return redirect(url_for('descuento.panel_descuento_home'))


@csrf.exempt
@bp.route("/eliminar/<int:id_descuento>", methods=["POST"])
def eliminar_descuento(id_descuento):
    try:
        if eliminar_descuento_sin_productos(id_descuento):
            flash(f"Descuento eliminado con éxito.", "success")
        else:
            flash(f"No se puede eliminar el descuento porque está asociado a productos.", "error")
    except Exception as e:
        flash(f"Error al intentar eliminar el descuento: {e}", "error")

    return redirect(url_for('descuento.panel_descuento_home'))

@csrf.exempt
@bp.route("/buscar_descuento", methods=["GET"])
def buscar_descuento():
    porcentaje = request.args.get("porcentaje", None)

    if porcentaje:
        try:
            descuentos = buscar_descuentos_por_porcentaje(porcentaje)
            if not descuentos:
                flash("No se encontraron descuentos relacionados con la búsqueda.", "error")
        except Exception as e:
            flash(f"Error al buscar descuentos: {e}", "error")
            descuentos = []
    else:
        descuentos = obtener_descuentos()

    return render_template("panel/descuento.html", descuentos=descuentos)

@csrf.exempt
@bp.route("/filtrar_descuento", methods=["GET"])
def filtrar_descuento():
    # Obtener el valor del filtro que combina estado y orden
    filtro_estado_orden = request.args.get("filtro_estado_orden", "todos")

    try:

        descuentos = obtener_descuentos_filtrados(filtro_estado_orden)
    except Exception as e:
        flash(f"Error al filtrar los descuentos: {e}", "error")
        descuentos = []

    return render_template('panel/descuento.html', descuentos=descuentos)


#APIS DE DESCUENTO

# OBTENER TODOS

@csrf.exempt
@bp.route("/api/descuentos", methods=["GET"])
@jwt_required()
def api_obtener_descuentos():
    rpta = dict()

    try:
        # Llamamos a la función que obtiene los descuentos desde la base de datos
        descuentos = obtener_descuentos()

        if not descuentos:
            rpta["data"] = {}
            rpta["message"] = "No se encontraron descuentos"
            rpta["status"] = 0
            return jsonify(rpta), 404  # Retornamos un código 404 si no hay descuentos

        # Serializamos los descuentos
        descuentos_serializados = [
            {
                "id_descuento": descuento[0],  # ID_DESCUENTO (índice 0)
                "porcentaje": descuento[1],    # PORCENTAJE (índice 1)
                "fecha_inicio": descuento[2],  # FECHA_INICIO (índice 2)
                "fecha_fin": descuento[3],     # FECHA_FIN (índice 3)
                "estado_descuento": descuento[4],  # ESTADO_DSCTO (índice 4)
                "fecha_agregacion": descuento[5]  # FECHA_AGREGACION (índice 5)
            }
            for descuento in descuentos
        ]

        # Si todo sale bien, retornamos los descuentos serializados
        rpta["data"] = descuentos_serializados
        rpta["message"] = "Descuentos obtenidos correctamente"
        rpta["status"] = 1
        return jsonify(rpta), 200  # Retornamos un código 200 con la respuesta

    except Exception as e:
        # Manejo de excepciones, para evitar caídas del servidor
        rpta["data"] = {}
        rpta["message"] = "Ocurrió un error: " + repr(e)
        rpta["status"] = 0
        return jsonify(rpta), 500


# OBTENER POR ID
@csrf.exempt
@bp.route("/api/descuentos/<int:id_descuento>", methods=["GET"])
@jwt_required()
def api_obtener_descuento_por_id(id_descuento):
    rpta = dict()

    try:
        # Obtener descuento por ID
        descuento = obtener_descuento_por_id(id_descuento)

        # Verificamos si descuento no existe
        if not descuento:
            rpta["data"] = {}
            rpta["message"] = "Descuento no encontrado"
            rpta["status"] = 0
            return jsonify(rpta), 404

        # Si `descuento` es una tupla, accedemos a los valores por su índice
        descuento_serializado = {
            "id_descuento": descuento[0],  # ID_DESCUENTO
            "porcentaje": descuento[1],    # PORCENTAJE
            "fecha_inicio": descuento[2],  # FECHA_INICIO
            "fecha_fin": descuento[3],     # FECHA_FIN
            "estado_descuento": descuento[4],  # ESTADO_DSCTO
            "fecha_agregacion": descuento[5]   # FECHA_AGREGACION
        }

        rpta["data"] = descuento_serializado
        rpta["message"] = "Descuento encontrado"
        rpta["status"] = 1
        return jsonify(rpta), 200

    except Exception as e:
        # Manejo de errores
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un error: {repr(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500

@csrf.exempt
@bp.route("/api/insertar_descuento", methods=["POST"])
@jwt_required()
def insertar_descuento_api():
    rpta = dict()

    # Verificamos si el usuario tiene los permisos necesarios (rol 1 en este caso)
    if current_user.is_authenticated and current_user.id_rol != 1:
        rpta["data"] = {}
        rpta["message"] = "No tienes permiso para realizar esta acción"
        rpta["status"] = 0
        return jsonify(rpta)

    try:
        # Obtenemos los datos enviados en el cuerpo de la solicitud
        data = request.get_json()

        if not data:
            rpta["data"] = {}
            rpta["message"] = "No se enviaron datos"
            rpta["status"] = 0
            return jsonify(rpta), 400

        # Extraemos los valores de los parámetros enviados en la solicitud
        porcentaje = data.get('porcentaje')
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        estado = data.get('estado')

        # Validamos si todos los campos necesarios fueron enviados
        if porcentaje is None or fecha_inicio is None or fecha_fin is None or estado is None:
            rpta["data"] = {}
            rpta["message"] = "Faltan datos requeridos"
            rpta["status"] = 0
            return jsonify(rpta), 400

        # Llamamos a la función insertar_descuento que debes tener implementada
        if insertar_descuento(porcentaje, fecha_inicio, fecha_fin, estado):
            rpta["data"] = {}
            rpta["message"] = "Descuento insertado correctamente"
            rpta["status"] = 1
            return jsonify(rpta), 200
        else:
            rpta["data"] = {}
            rpta["message"] = "Error al insertar el descuento"
            rpta["status"] = 0
            return jsonify(rpta), 500

    except Exception as e:
        # Manejo de errores
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un error: {repr(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500

@csrf.exempt
@bp.route("/api/modificar_descuento", methods=["POST"])
@jwt_required()
def modificar_descuento_api():
    rpta = dict()

    # Verificamos si el usuario tiene el rol adecuado (asumimos que el rol 1 tiene permisos)
    if current_user.is_authenticated and current_user.id_rol != 1:
        rpta["data"] = {}
        rpta["message"] = "No tienes permiso para realizar esta acción"
        rpta["status"] = 0
        return jsonify(rpta), 403  # Retornamos un código 403 si no tiene permisos

    try:
        # Obtenemos los datos de la solicitud
        data = request.get_json()

        if not data:
            rpta["data"] = {}
            rpta["message"] = "No se enviaron datos"
            rpta["status"] = 0
            return jsonify(rpta), 400  # Si no se enviaron datos, retornamos un código 400

        # Datos necesarios para modificar el descuento
        id_descuento = data.get('id_descuento')
        porcentaje = data.get('porcentaje')
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        estado = data.get('estado')

        # Validamos que se enviaron los datos requeridos
        if not id_descuento or porcentaje is None or not fecha_inicio or not fecha_fin or not estado:
            rpta["data"] = {}
            rpta["message"] = "Faltan datos requeridos"
            rpta["status"] = 0
            return jsonify(rpta), 400  # Si faltan datos, retornamos un código 400

        # Llamamos al método para modificar el descuento
        if actualizar_descuento(id_descuento, porcentaje, fecha_inicio, fecha_fin, estado):
            rpta["data"] = {}
            rpta["message"] = "Descuento modificado correctamente"
            rpta["status"] = 1
            return jsonify(rpta), 200  # Retornamos un código 200 si la modificación fue exitosa
        else:
            rpta["data"] = {}
            rpta["message"] = "Error al modificar el descuento"
            rpta["status"] = 0
            return jsonify(rpta), 500  # Retornamos un código 500 si hubo un error

    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un error: {repr(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500  # Retornamos un código 500 si hubo una excepción


@csrf.exempt
@bp.route("/api/eliminar_descuento", methods=["POST"])
@jwt_required()
def eliminar_descuento_api():
    rpta = dict()

    # Verificamos si el usuario tiene el rol adecuado (asumimos que el rol 1 tiene permisos)
    if current_user.is_authenticated and current_user.id_rol != 1:
        rpta["data"] = {}
        rpta["message"] = "No tienes permiso para realizar esta acción"
        rpta["status"] = 0
        return jsonify(rpta), 403  # Retornamos un código 403 si no tiene permisos

    try:
        # Obtenemos los datos de la solicitud
        data = request.get_json()

        if not data:
            rpta["data"] = {}
            rpta["message"] = "No se enviaron datos"
            rpta["status"] = 0
            return jsonify(rpta), 400  # Si no se enviaron datos, retornamos un código 400

        # Obtenemos el ID del descuento a eliminar
        id_descuento = data.get('id_descuento')

        # Validamos que se haya enviado el id_descuento
        if not id_descuento:
            rpta["data"] = {}
            rpta["message"] = "Falta el id_descuento"
            rpta["status"] = 0
            return jsonify(rpta), 400

        # Llamamos a la función que elimina el descuento
        if eliminar_descuento_sin_productos(id_descuento):
            rpta["data"] = {}
            rpta["message"] = "Descuento eliminado correctamente"
            rpta["status"] = 1
            return jsonify(rpta), 200
        else:
            rpta["data"] = {}
            rpta["message"] = "Error al eliminar el descuento o está asociado a productos"
            rpta["status"] = 0
            return jsonify(rpta), 500

    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un problema: {repr(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500


@csrf.exempt
@bp.route("/api/resenas", methods=["GET"])
@jwt_required()
def api_obtener_resenas():
    rpta = dict()

    try:
        # Llamamos a la función que obtiene las reseñas desde la base de datos
        resenas = obtener_todas_resenas()

        if not resenas:
            rpta["data"] = {}
            rpta["message"] = "No se encontraron reseñas"
            rpta["status"] = 0
            return jsonify(rpta), 404  # Retornamos un código 404 si no hay reseñas

        # Serializamos las reseñas
        resenas_serializadas = [
            {
                "id_resena": resena[0],  # ID_RESENA (índice 0)
                "id_producto": resena[1],  # ID_PRODUCTO (índice 1)
                "id_usuario": resena[2],  # ID_USUARIO (índice 2)
                "puntaje": resena[3],     # PUNTUACION (índice 3)
                "comentario": resena[4],  # COMENTARIO (índice 4)
                "fecha_resena": resena[5], # FECHA_RESENA (índice 5)
                "estado": resena[6],      # ESTADO (índice 6)
                "fecha_agregacion": resena[7]  # FECHA_AGREGACION (índice 7)
            }
            for resena in resenas
        ]

        # Si todo sale bien, retornamos las reseñas serializadas
        rpta["data"] = resenas_serializadas
        rpta["message"] = "Reseñas obtenidas correctamente"
        rpta["status"] = 1
        return jsonify(rpta), 200  # Retornamos un código 200 con la respuesta

    except Exception as e:
        # Manejo de errores
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un error: {repr(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500

@csrf.exempt
@bp.route("/api/resenas/<int:id_resena>", methods=["GET"])
@jwt_required()
def api_obtener_resena_por_id(id_resena):
    rpta = dict()

    try:
        # Llamamos a la función que obtiene la reseña por ID
        resena = obtener_resena_por_id(id_resena)

        if not resena:
            rpta["data"] = {}
            rpta["message"] = "Reseña no encontrada"
            rpta["status"] = 0
            return jsonify(rpta), 404  # Retornamos un código 404 si no se encuentra la reseña

        # Serializamos la reseña
        resena_serializada = {
            "id_resena": resena[0],
            "id_producto": resena[1],
            "id_usuario": resena[2],
            "puntaje": resena[3],
            "comentario": resena[4],
            "fecha_resena": resena[5],
            "estado": resena[6],
            "fecha_agregacion": resena[7]
        }

        # Si todo sale bien, retornamos la reseña serializada
        rpta["data"] = resena_serializada
        rpta["message"] = "Reseña encontrada"
        rpta["status"] = 1
        return jsonify(rpta), 200  # Retornamos un código 200 con la respuesta

    except Exception as e:
        # Manejo de errores
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un error: {repr(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500


@csrf.exempt
@bp.route("/api/insertar_resena", methods=["POST"])
@jwt_required()
def api_insertar_resena():
    rpta = dict()

    try:
        data = request.get_json()

        if not data:
            rpta["data"] = {}
            rpta["message"] = "No se enviaron datos"
            rpta["status"] = 0
            return jsonify(rpta), 400

        # Extraemos los datos del cuerpo de la solicitud
        id_producto = data.get('id_producto')
        id_usuario = data.get('id_usuario')
        puntuacion = data.get('puntuacion')
        comentario = data.get('comentario')
        fecha_resena = data.get('fecha_resena')
        estado = data.get('estado', 'A')  # Por defecto, el estado es 'A' (Activo)

        # Validación de los datos recibidos
        if not id_producto or not id_usuario or not puntuacion or not comentario or not fecha_resena:
            rpta["data"] = {}
            rpta["message"] = "Faltan datos requeridos"
            rpta["status"] = 0
            return jsonify(rpta), 400

        # Llamamos al método de inserción
        if insertar_resena(id_producto, id_usuario, puntuacion, comentario, fecha_resena, estado):
            rpta["data"] = {}
            rpta["message"] = "Reseña insertada correctamente"
            rpta["status"] = 1
            return jsonify(rpta), 200
        else:
            rpta["data"] = {}
            rpta["message"] = "Error al insertar la reseña"
            rpta["status"] = 0
            return jsonify(rpta), 500

    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un error: {repr(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500

@csrf.exempt
@bp.route("/api/modificar_resena", methods=["POST"])
@jwt_required()
def api_modificar_resena():
    rpta = dict()

    try:
        data = request.get_json()

        if not data:
            rpta["data"] = {}
            rpta["message"] = "No se enviaron datos"
            rpta["status"] = 0
            return jsonify(rpta), 400

        id_resena = data.get('id_resena')
        id_producto = data.get('id_producto')
        id_usuario = data.get('id_usuario')
        puntuacion = data.get('puntuacion')
        comentario = data.get('comentario')
        fecha_resena = data.get('fecha_resena')
        estado = data.get('estado')

        if not id_resena or not id_producto or not id_usuario or puntuacion is None or not comentario or not fecha_resena or not estado:
            rpta["data"] = {}
            rpta["message"] = "Faltan datos requeridos"
            rpta["status"] = 0
            return jsonify(rpta), 400

        if modificar_resena(id_resena, id_producto, id_usuario, puntuacion, comentario, fecha_resena, estado):
            rpta["data"] = {}
            rpta["message"] = "Reseña modificada correctamente"
            rpta["status"] = 1
            return jsonify(rpta), 200
        else:
            rpta["data"] = {}
            rpta["message"] = "Error al modificar la reseña"
            rpta["status"] = 0
            return jsonify(rpta), 500

    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un error: {repr(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500

@csrf.exempt
@bp.route("/api/eliminar_resena", methods=["POST"])
@jwt_required()
def api_eliminar_resena():
    rpta = dict()

    try:
        data = request.get_json()

        if not data:
            rpta["data"] = {}
            rpta["message"] = "No se enviaron datos"
            rpta["status"] = 0
            return jsonify(rpta), 400

        id_resena = data.get('id_resena')

        if not id_resena:
            rpta["data"] = {}
            rpta["message"] = "Falta el id_resena"
            rpta["status"] = 0
            return jsonify(rpta), 400

        if eliminar_resena(id_resena):
            rpta["data"] = {}
            rpta["message"] = "Reseña eliminada correctamente"
            rpta["status"] = 1
            return jsonify(rpta), 200
        else:
            rpta["data"] = {}
            rpta["message"] = "Error al eliminar la reseña"
            rpta["status"] = 0
            return jsonify(rpta), 500

    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un problema: {repr(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500




