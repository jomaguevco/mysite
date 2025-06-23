from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from flask_jwt_extended import jwt_required, get_jwt_identity
from .control_ventas import *
from app import csrf


bp = Blueprint('ventas', __name__, url_prefix='/ventas')


@csrf.exempt
@bp.route('/panel_ventas_home')
def panel_ventas_home():
    if current_user.id_rol != 1:
        flash('No tienes permiso para acceder a esta página', 'error')
        return redirect(url_for('home.index'))

    ventas = obtenerTodasVentas()
    return render_template('panel/comprobante.html', ventas=ventas)

                                ### APIS TABLA VENTA ###

### API filtrar ventas general###
@csrf.exempt
@bp.route("/api/ventas", methods=["GET"])

def api_obtener_ventas():
    rpta = dict()

    # Comprobamos si el rol del usuario es diferente a 1
    if current_user.is_authenticated and current_user.id_rol != 1:
        rpta["data"] = {}
        rpta["message"] = "No tienes permiso para acceder a esta información"
        rpta["status"] = 0
        return jsonify(rpta), 403  # Retornamos un código 403 si no tiene permisos

    try:
        ventas = obtenerTodasVentas()

        if not ventas:
            rpta["data"] = {}
            rpta["message"] = "No se encontraron ventas"
            rpta["status"] = 0
            return jsonify(rpta), 404  # Retornamos un código 404 si no hay ventas

        # Serializamos las ventas
        ventas_serializadas = [
            {
                "id": venta["ID_VENTA"],
                "nombre_completo": venta["NOMBRE_COMPLETO"],
                "fecha_hora": venta["FECHA_HORA"],
                "total": venta["TOTAL"]
            }
            for venta in ventas
        ]

        # Si todo sale bien, retornamos las ventas serializadas
        rpta["data"] = ventas_serializadas
        rpta["message"] = "Ventas obtenidas correctamente"
        rpta["status"] = 1
        return jsonify(rpta), 200  # Retornamos un código 200 con la respuesta

    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = f"Error al obtener las ventas: {str(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500  # Retornamos un código 500 si hay un error


### API filtrar venta por ID ###
@csrf.exempt
@bp.route("/api/venta/<int:id_venta>", methods=["GET"])
@jwt_required()
def api_obtener_venta_por_id(id_venta):
    rpta = dict()

    # Comprobamos si el usuario no está autenticado o su rol es diferente a 1
    if current_user.is_authenticated and current_user.id_rol != 1:
        rpta["data"] = {}
        rpta["message"] = "No tienes permiso para acceder a esta información"
        rpta["status"] = 0
        return jsonify(rpta), 403  # Retornamos un código 403 si no tiene permisos

    try:
        venta = obtenerVentaPorID(id_venta)

        if not venta:
            rpta["data"] = {}
            rpta["message"] = "Venta no encontrada"
            rpta["status"] = 0
            return jsonify(rpta), 404  # Retornamos un código 404 si no se encuentra la venta

        # Serializamos la venta
        venta_serializada = {
            "id": venta["ID_VENTA"],
            "nombre_completo": venta["NOMBRE_COMPLETO"],
            "fecha_hora": venta["FECHA_HORA"],
            "total": venta["TOTAL"]
        }

        rpta["data"] = venta_serializada
        rpta["message"] = "Venta encontrada"
        rpta["status"] = 1
        return jsonify(rpta), 200  # Retornamos la venta serializada con un código 200

    except Exception as e:
        # Manejo de errores
        rpta["data"] = {}
        rpta["message"] = f"Error al obtener la venta: {str(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500  # Retornamos un código 500 si ocurre un error en el proceso



### API registrar venta ###
@csrf.exempt
@bp.route("/api/insertar_venta", methods=["POST"])
@jwt_required()
def insertar_venta_api():
    rpta = dict()

    if current_user.is_authenticated and current_user.id_rol != 1:
        rpta["data"] = {}
        rpta["message"] = "No tienes permiso para realizar esta acción"
        rpta["status"] = 0
        return jsonify(rpta)

    try:
        data = request.get_json()

        if not data:
            rpta["data"] = {}
            rpta["message"] = "No se enviaron datos"
            rpta["status"] = 0
            return jsonify(rpta), 400

        id_usuario = data.get('id_usuario')
        id_tarjeta = data.get('id_tarjeta')
        subtotal = data.get('subtotal')

        if not id_usuario or not id_tarjeta or subtotal is None:
            rpta["data"] = {}
            rpta["message"] = "Faltan datos requeridos"
            rpta["status"] = 0
            return jsonify(rpta), 400

        if insertar_venta(id_usuario, id_tarjeta, subtotal):
            rpta["data"] = {}
            rpta["message"] = "Venta realizada correctamente"
            rpta["status"] = 1
            return jsonify(rpta), 200
        else:
            rpta["data"] = {}
            rpta["message"] = "Error al insertar la venta"
            rpta["status"] = 0
            return jsonify(rpta), 500

    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un problema: {repr(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500


### API modificar venta ###
@csrf.exempt
@bp.route("/api/modificar_venta", methods=["POST"])
@jwt_required()
def modificar_venta_api():
    rpta = dict()

    if current_user.is_authenticated and current_user.id_rol != 1:
        rpta["data"] = {}
        rpta["message"] = "No estás autenticado"
        rpta["status"] = 0
        return jsonify(rpta), 401

    try:
        data = request.get_json()

        if not data:
            rpta["data"] = {}
            rpta["message"] = "No se enviaron datos"
            rpta["status"] = 0
            return jsonify(rpta), 400

        id_venta = data.get('id_venta')
        id_usuario = data.get('id_usuario')
        id_tarjeta = data.get('id_tarjeta')
        subtotal = data.get('subtotal')

        if not id_venta or not id_usuario or not id_tarjeta or subtotal is None:
            rpta["data"] = {}
            rpta["message"] = "Faltan datos requeridos"
            rpta["status"] = 0
            return jsonify(rpta), 400

        if modificar_venta(id_venta, id_usuario, id_tarjeta, subtotal):
            rpta["data"] = {}
            rpta["message"] = "Venta modificada correctamente"
            rpta["status"] = 1
            return jsonify(rpta), 200
        else:
            rpta["data"] = {}
            rpta["message"] = "Error al modificar la venta"
            rpta["status"] = 0
            return jsonify(rpta), 500

    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un problema: {repr(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500


### API eliminar venta ###
@csrf.exempt
@bp.route("/api/eliminar_venta", methods=["POST"])

def eliminar_venta_api():
    rpta = dict()

    if current_user.is_authenticated and current_user.id_rol != 1:
        rpta["data"] = {}
        rpta["message"] = "No estás autenticado"
        rpta["status"] = 0
        return jsonify(rpta), 401

    try:
        data = request.get_json()

        if not data:
            rpta["data"] = {}
            rpta["message"] = "No se enviaron datos"
            rpta["status"] = 0
            return jsonify(rpta), 400

        id_venta = data.get('id_venta')

        if not id_venta:
            rpta["data"] = {}
            rpta["message"] = "Falta el id_venta"
            rpta["status"] = 0
            return jsonify(rpta), 400

        if eliminar_venta(id_venta):
            rpta["data"] = {}
            rpta["message"] = "Venta eliminada correctamente"
            rpta["status"] = 1
            return jsonify(rpta), 200
        else:
            rpta["data"] = {}
            rpta["message"] = "Error al eliminar la venta"
            rpta["status"] = 0
            return jsonify(rpta), 500

    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un problema: {repr(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500




                                ### APIS TABLA DETALLE_VENTA ###

### API filtrar detalle_venta general###
@csrf.exempt
@bp.route('/api/detalle_ventas', methods=['GET'])
@jwt_required()
def obtener_detalle_ventas():
    rpta = dict()

    if current_user.is_authenticated and current_user.id_rol != 1:
        rpta["data"] = {}
        rpta["message"] = "No tienes permiso para acceder a esta información"
        rpta["status"] = 0
        return jsonify(rpta), 403

    try:
        detalles = obtenerTodosDetalleVenta()

        if not detalles:
            rpta["data"] = {}
            rpta["message"] = "No se encontraron detalles"
            rpta["status"] = 0
            return jsonify(rpta), 404

        detalles_serializados = [
            {
                "id_venta": detalle["ID_VENTA"],
                "id_tipo_producto": detalle["ID_TIPO_PRODUCTO"],
                "id_producto": detalle["ID_PRODUCTO"],
                "producto": detalle["NOMBRE_PRODUCTO"],
                "cantidad": detalle["CANTIDAD"],
                "precio": detalle["PRECIO"],
                "subtotal": detalle["SUBTOTAL"],
                "estado": detalle["ESTADO"]
            }
            for detalle in detalles
        ]

        rpta["data"] = detalles_serializados
        rpta["message"] = "Detalles obtenidos correctamente"
        rpta["status"] = 1
        return jsonify(rpta), 200

    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = f"Error al obtener los detalles: {str(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500


### API filtrar detalle_venta por ID ###
@csrf.exempt
@bp.route('/api/detalle_ventas/<int:id_venta>/<int:id_tipo_producto>/<int:id_producto>', methods=['GET'])
@jwt_required()
def obtener_detalle_ventas_filtrados(id_venta, id_tipo_producto, id_producto):
    rpta = dict()

    if current_user.is_authenticated and current_user.id_rol != 1:
        rpta["data"] = {}
        rpta["message"] = "No tienes permiso para acceder a esta información"
        rpta["status"] = 0
        return jsonify(rpta), 403

    try:
        detalles = obtenerDetalleFiltrado(id_venta, id_tipo_producto, id_producto)

        if not detalles:
            rpta["data"] = {}
            rpta["message"] = "No se encontraron detalles con los filtros proporcionados"
            rpta["status"] = 0
            return jsonify(rpta), 404

        detalles_serializados = [
            {
                "id_venta": detalle["ID_VENTA"],
                "id_tipo_producto": detalle["ID_TIPO_PRODUCTO"],
                "id_producto": detalle["ID_PRODUCTO"],
                "producto": detalle["NOMBRE_PRODUCTO"],
                "cantidad": detalle["CANTIDAD"],
                "precio": detalle["PRECIO"],
                "subtotal": detalle["SUBTOTAL"],
                "estado": detalle["ESTADO"]
            }
            for detalle in detalles
        ]

        rpta["data"] = detalles_serializados
        rpta["message"] = "Detalles filtrados obtenidos correctamente"
        rpta["status"] = 1
        return jsonify(rpta), 200

    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = f"Error al obtener los detalles filtrados: {str(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500



### API registrar detalle_venta ###
@csrf.exempt
@bp.route("/api/insertar_detalle", methods=["POST"])
@jwt_required()
def insertar_detalle_api():
    rpta = dict()

    if current_user.is_authenticated and current_user.id_rol != 1:
        rpta["data"] = {}
        rpta["message"] = "No tienes permiso para realizar esta acción"
        rpta["status"] = 0
        return jsonify(rpta), 403

    try:
        data = request.get_json()

        if not data:
            rpta["data"] = {}
            rpta["message"] = "No se enviaron datos"
            rpta["status"] = 0
            return jsonify(rpta), 400

        id_venta = data.get('id_venta')
        id_tipo_producto = data.get('id_tipo_producto')
        id_producto = data.get('id_producto')
        cantidad = data.get('cantidad')
        precio = data.get('precio')

        if not id_venta or not id_tipo_producto or not id_producto or cantidad is None or precio is None:
            rpta["data"] = {}
            rpta["message"] = "Faltan datos requeridos"
            rpta["status"] = 0
            return jsonify(rpta), 400

        if insertar_detalle(id_venta, id_tipo_producto, id_producto, cantidad, precio):
            rpta["data"] = {}
            rpta["message"] = "Detalle de venta insertado correctamente"
            rpta["status"] = 1
            return jsonify(rpta), 200
        else:
            rpta["data"] = {}
            rpta["message"] = "Error al insertar el detalle de venta"
            rpta["status"] = 0
            return jsonify(rpta), 500

    except Exception as e:
        # Manejo de errores generales
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un problema: {repr(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500


### API modificar detalle_venta ###
@csrf.exempt
@bp.route("/api/modificar_detalle", methods=["POST"])
@jwt_required()
def modificar_detalle_api():
    rpta = dict()

    if current_user.is_authenticated and current_user.id_rol != 1:
        rpta["data"] = {}
        rpta["message"] = "No tienes permiso para realizar esta acción"
        rpta["status"] = 0
        return jsonify(rpta), 403

    try:
        data = request.get_json()

        if not data:
            rpta["data"] = {}
            rpta["message"] = "No se enviaron datos"
            rpta["status"] = 0
            return jsonify(rpta), 400

        id_venta = data.get('id_venta')
        id_tipo_producto = data.get('id_tipo_producto')
        id_producto = data.get('id_producto')
        cantidad = data.get('cantidad')
        precio = data.get('precio')

        if not id_venta or not id_tipo_producto or not id_producto or cantidad is None or precio is None:
            rpta["data"] = {}
            rpta["message"] = "Faltan datos requeridos"
            rpta["status"] = 0
            return jsonify(rpta), 400

        if actualizarDetalleVenta(id_venta, id_tipo_producto, id_producto, cantidad, precio):
            rpta["data"] = {}
            rpta["message"] = "Detalle de venta modificado correctamente"
            rpta["status"] = 1
            return jsonify(rpta), 200
        else:
            rpta["data"] = {}
            rpta["message"] = "Error al modificar el detalle de venta"
            rpta["status"] = 0
            return jsonify(rpta), 500

    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un problema: {repr(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500


### API eliminar detalle_venta ###
@csrf.exempt
@bp.route("/api/eliminar_detalle", methods=["POST"])
@jwt_required()
def eliminar_detalle_api():
    rpta = dict()

    if current_user.is_authenticated and current_user.id_rol != 1:
        rpta["data"] = {}
        rpta["message"] = "No tienes permiso para realizar esta acción"
        rpta["status"] = 0
        return jsonify(rpta), 403

    try:
        data = request.get_json()

        if not data:
            rpta["data"] = {}
            rpta["message"] = "No se enviaron datos"
            rpta["status"] = 0
            return jsonify(rpta), 400

        id_venta = data.get('id_venta')
        id_tipo_producto = data.get('id_tipo_producto')
        id_producto = data.get('id_producto')

        if not id_venta or not id_tipo_producto or not id_producto:
            rpta["data"] = {}
            rpta["message"] = "Faltan datos requeridos"
            rpta["status"] = 0
            return jsonify(rpta), 400

        if eliminarDetalleVenta(id_venta, id_tipo_producto, id_producto):
            rpta["data"] = {}
            rpta["message"] = "Detalle de venta eliminado correctamente"
            rpta["status"] = 1
            return jsonify(rpta), 200
        else:
            rpta["data"] = {}
            rpta["message"] = "Error al eliminar el detalle de venta"
            rpta["status"] = 0
            return jsonify(rpta), 500

    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un problema: {repr(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500
