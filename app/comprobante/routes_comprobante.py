from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app import csrf
from .control_comprobante import obtenerTodosComprobantes, obtenerProductosPorComprobante, dar_baja_comprobante,eliminar_comprobante,modificar_comprobante
from app.bd import get_db_connection
import pymysql
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('comprobante', __name__, url_prefix='/comprobante')

@csrf.exempt
@bp.route('/panel_comprobantes_home')
def panel_comprobantes_home():

    if current_user.id_rol != 1:
        flash('No tienes permiso para acceder a esta página', 'error')
        return redirect(url_for('home.index'))

    comprobantes = obtenerTodosComprobantes()
    return render_template('panel/comprobante.html', comprobantes=comprobantes)

@csrf.exempt
@bp.route('/productos/<int:id_comprobante>', methods=['GET'])
def obtener_productos(id_comprobante):

    try:
        productos = obtenerProductosPorComprobante(id_comprobante)
        return jsonify(productos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@csrf.exempt
@bp.route('/detalle/<int:id_comprobante>', methods=['GET'])
def detalle_comprobante(id_comprobante):

    if current_user.id_rol != 1:
        flash('No tienes permiso para acceder a esta página', 'error')
        return redirect(url_for('home.index'))

    productos = obtenerProductosPorComprobante(id_comprobante)
    return render_template('panel/detalle_comprobante.html', productos=productos, id_comprobante=id_comprobante)

@csrf.exempt
@bp.route('/dar_baja/<int:id_comprobante>', methods=['POST'])
def dar_baja_comprobante_ruta(id_comprobante):

    resultado = dar_baja_comprobante(id_comprobante)


    if resultado["success"]:
        flash('El comprobante ha sido dado de baja exitosamente.', 'success')
    else:

        flash(f'Ocurrió un error: {resultado["message"]}', 'error')


    return redirect(url_for('comprobante.panel_comprobantes_home'))



@csrf.exempt
@bp.route('/api/comprobantes', methods=['GET'])
@jwt_required()
def api_obtener_comprobantes():
    estado = request.args.get('estado')

    try:
        if estado not in [None, 'A', 'I']:
            return jsonify({'error': 'Estado inválido. Usa "A" para activos o "I" para inactivos.'}), 400

        # Llamamos a obtenerTodosComprobantes y pasamos el estado
        comprobantes = obtenerTodosComprobantes(estado)
        return jsonify(comprobantes), 200
    except Exception as e:
        return jsonify({'error': f'Error al obtener comprobantes: {str(e)}'}), 500


@csrf.exempt
@bp.route("/api/productos_comprobante/<int:id_comprobante>", methods=["GET"])
@jwt_required()
def api_obtener_productos_por_comprobante(id_comprobante):
    rpta = dict()

    try:
        # Llamamos al método para obtener los productos del comprobante
        productos = obtenerProductosPorComprobante(id_comprobante)

        if not productos:
            rpta["data"] = []
            rpta["message"] = "No se encontraron productos para el comprobante"
            rpta["status"] = 0
            return jsonify(rpta), 404  # Retornamos un código 404 si no hay productos

        # Serializamos los productos
        productos_serializados = [
            {
                "nombre_producto": producto["NOMBRE_PRODUCTO"],
                "descripcion": producto["DESCRIPCION"],
                "cantidad": producto["CANTIDAD"],
                "subtotal": producto["SUBTOTAL"]
            }
            for producto in productos
        ]

        # Si todo sale bien, retornamos los productos serializados
        rpta["data"] = productos_serializados
        rpta["message"] = "Productos obtenidos correctamente"
        rpta["status"] = 1
        return jsonify(rpta), 200  # Retornamos un código 200 con la respuesta

    except Exception as e:
        # Manejo de errores
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un error: {repr(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500  # Retornamos un código 500 si ocurre un error

@csrf.exempt
@bp.route("/api/comprobante/baja", methods=["POST"])
@jwt_required()
def api_dar_baja_comprobante():
    rpta = dict()

    try:
        # Obtenemos los datos del body (json) enviado en la petición
        data = request.get_json()
        id_comprobante = data.get('id_comprobante')

        if not id_comprobante:
            rpta["data"] = {}
            rpta["message"] = "El parámetro id_comprobante es obligatorio"
            rpta["status"] = 0
            return jsonify(rpta), 400  # Retornamos un código 400 si falta el id_comprobante

        # Llamamos al método dar_baja_comprobante y capturamos su resultado
        resultado = dar_baja_comprobante(id_comprobante)

        if resultado["success"]:  # Si el resultado es exitoso
            rpta["data"] = {}
            rpta["message"] = "Comprobante dado de baja exitosamente."
            rpta["status"] = 1
            return jsonify(rpta), 200  # Código 200 para éxito

        # Si el resultado no es exitoso (comprobante no encontrado o algún otro error)
        rpta["data"] = {}
        rpta["message"] = resultado["message"]
        rpta["status"] = 0
        return jsonify(rpta), 400  # Retornamos un código 400 para errores

    except Exception as e:
        # Si ocurre un error en el proceso
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un error inesperado: {repr(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500  # Código 500 para errores internos del servidor


@csrf.exempt
@bp.route('/api/comprobante/eliminar', methods=['POST'])
@jwt_required()
def api_eliminar_comprobante():
    rpta = dict()

    try:
        # Obtener el id_comprobante desde el cuerpo de la solicitud
        data = request.get_json()
        id_comprobante = data.get('id_comprobante')

        if not id_comprobante:
            rpta["data"] = {}
            rpta["message"] = "El ID del comprobante es requerido."
            rpta["status"] = 0
            return jsonify(rpta), 400  # Si no se pasa el id_comprobante, se retorna un error 400

        # Llamamos al método eliminar_comprobante
        success, message = eliminar_comprobante(id_comprobante)

        if not success:
            rpta["data"] = {}
            rpta["message"] = message
            rpta["status"] = 0
            return jsonify(rpta), 400  # En caso de error, retornamos 400

        # Si la operación fue exitosa
        rpta["data"] = {}
        rpta["message"] = message
        rpta["status"] = 1
        return jsonify(rpta), 200  # Retornamos un código 200 de éxito

    except Exception as e:
        # En caso de algún error no manejado
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un error inesperado: {str(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500  # Retornamos un error 500


@csrf.exempt
@bp.route('/api/comprobante/modificar', methods=['POST'])
@jwt_required()
def api_modificar_comprobante():
    rpta = dict()

    try:
        # Obtendremos los datos del body (id_comprobante y tipo_comprobante)
        datos = request.get_json()
        id_comprobante = datos.get('id_comprobante')
        nuevo_tipo_comprobante = datos.get('nuevo_tipo_comprobante')

        # Validamos que se haya enviado el ID y tipo de comprobante
        if not id_comprobante or not nuevo_tipo_comprobante:
            return jsonify({'message': 'El id_comprobante y nuevo_tipo_comprobante son requeridos.'}), 400

        # Llamamos al método de modificación del comprobante
        success, message = modificar_comprobante(id_comprobante, nuevo_tipo_comprobante)

        if not success:
            rpta["data"] = {}
            rpta["message"] = message
            rpta["status"] = 0
            return jsonify(rpta), 400  # En caso de error, retornamos 400

        # Si la operación fue exitosa
        rpta["data"] = {}
        rpta["message"] = message
        rpta["status"] = 1
        return jsonify(rpta), 200  # Retornamos un código 200 de éxito

    except Exception as e:
        # En caso de algún error no manejado
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un error inesperado: {str(e)}"
        rpta["status"] = 0
        return jsonify(rpta), 500  # Retornamos un error 500

