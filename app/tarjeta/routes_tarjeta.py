from flask import Blueprint, jsonify, request
from flask_login import current_user
from .control_tarjeta import obtener_todas_tarjetas, obtener_tarjeta_id, insertar_tarjeta, modificar_tarjeta, eliminar_tarjeta

from app import csrf

from flask_jwt_extended import jwt_required

bp = Blueprint('tarjeta', __name__, url_prefix='/tarjeta')

@bp.route('/api_obtener_tarjetas', methods=['GET'])
@csrf.exempt
@jwt_required()
def api_obtener_tarjetas():
    if current_user.is_authenticated and current_user.id_rol != 1:
        return jsonify({
            "data": [],
            "message": "No tienes permiso para realizar esta acción",
            "status": 403
        }), 403

    tarjetas = obtener_todas_tarjetas()
    return jsonify({
        "data": tarjetas,
        "message": "Tarjetas obtenidas exitosamente",
        "status": 200
    })


@bp.route('/api_obtener_tarjeta_id', methods=['GET'])
@csrf.exempt
@jwt_required()
def api_obtener_tarjeta_id():
    """Obtiene una tarjeta por su ID"""
    if current_user.is_authenticated and current_user.id_rol != 1:
        return jsonify({
            "data": [],
            "message": "No tienes permiso para acceder a esta información",
            "status": 0
        }), 403

    id_tarjeta = request.json.get("id_tarjeta")

    tarjeta = obtener_tarjeta_id(id_tarjeta)
    if not tarjeta:
        return jsonify({
            "data": [],
            "message": "Tarjeta no encontrada",
            "status": 0
        }), 404

    tarjeta_rpta = {
        "id_tarjeta": tarjeta["ID_TARJETA"],
        "id_usuario": tarjeta["ID_USUARIO"],
        "tipo_tarjeta": tarjeta["TIPO_TARJETA"],
        "numero_tarjeta": tarjeta["NUMERO_TARJETA"],
        "fecha_expiracion": tarjeta["FECHA_EXPIRACION"]
    }
    return jsonify({
        "data": tarjeta_rpta,
        "message": "Tarjeta obtenida correctamente",
        "status": 1
    }), 200


@bp.route('/api_insertar_tarjeta', methods=['POST'])
@csrf.exempt
@jwt_required()
def api_insertar_tarjeta():
    """Inserta una nueva tarjeta a la base de datos"""
    if current_user.is_authenticated and current_user.id_rol != 1:
        return jsonify({
            "data": [],
            "message": "No tienes permiso para acceder a esta información",
            "status": 0
        }), 403

    data = request.get_json()
    if not data:
        return jsonify({
            "data": [],
            "message": "Faltan datos",
            "status": 0
        }), 400

    try:
        # Extraer datos del cuerpo de la solicitud
        id_usuario = data['id_usuario']
        tipo_tarjeta = data['tipo_tarjeta']
        numero_tarjeta = data['numero_tarjeta']
        fecha_expiracion = data['fecha_expiracion']
        cvv = data['cvv']

        # Llamar a la función para insertar la tarjeta y obtener su ID
        id_tarjeta = insertar_tarjeta(id_usuario, tipo_tarjeta, numero_tarjeta, fecha_expiracion, cvv)

        # Responder con éxito e incluir el ID de la tarjeta creada o existente
        return jsonify({
            "data": {"id_tarjeta": id_tarjeta},
            "message": "Tarjeta creada o recuperada con éxito",
            "status": 1
        }), 201
    except KeyError as e:
        # Manejar errores de datos faltantes
        return jsonify({
            "data": [],
            "message": f"Faltan datos: {str(e)}",
            "status": 0
        }), 400
    except Exception as e:
        # Manejar cualquier otro error
        return jsonify({
            "data": [],
            "message": f"Error al crear la tarjeta: {str(e)}",
            "status": 0
        }), 500


@bp.route('/api_modificar_tarjeta', methods=['POST'])
@csrf.exempt
@jwt_required()
def api_modificar_tarjeta():
    """Modifica una tarjeta existente"""
    if current_user.is_authenticated and current_user.id_rol != 1:
        return jsonify({
            "data": [],
            "message": "No tienes permiso para acceder a esta información",
            "status": 0
        }), 403

    data = request.get_json()
    if not data or 'id_tarjeta' not in data:
        return jsonify({
            "data": [],
            "message": "Faltan datos",
            "status": 0
        }), 400

    try:
        id_tarjeta = data['id_tarjeta']
        tipo_tarjeta = data.get('tipo_tarjeta')
        numero_tarjeta = data.get('numero_tarjeta')
        fecha_expiracion = data.get('fecha_expiracion')
        cvv = data.get('cvv')

        # Llamar a la función para modificar la tarjeta
        modificar_tarjeta(id_tarjeta, tipo_tarjeta, numero_tarjeta, fecha_expiracion, cvv)

        return jsonify({
            "data": [],
            "message": "Tarjeta modificada con éxito",
            "status": 1
        }), 200
    except ValueError as e:
        return jsonify({
            "data": [],
            "message": str(e),
            "status": 0
        }), 404
    except Exception as e:
        return jsonify({
            "data": [],
            "message": f"Error al modificar la tarjeta: {str(e)}",
            "status": 0
        }), 500


@bp.route('/api_eliminar_tarjeta', methods=['POST'])
@csrf.exempt
@jwt_required()
def api_eliminar_tarjeta():
    """Elimina (desactiva) una tarjeta existente"""
    if current_user.is_authenticated and current_user.id_rol != 1:
        return jsonify({
            "data": [],
            "message": "No tienes permiso para acceder a esta información",
            "status": 0
        }), 403

    data = request.get_json()
    if not data or 'id_tarjeta' not in data:
        return jsonify({
            "data": [],
            "message": "Faltan datos",
            "status": 0
        }), 400

    try:
        id_tarjeta = data['id_tarjeta']

        # Llamar a la función para eliminar la tarjeta
        eliminar_tarjeta(id_tarjeta)

        return jsonify({
            "data": [],
            "message": "Tarjeta eliminada con éxito",
            "status": 1
        }), 200
    except ValueError as e:
        return jsonify({
            "data": [],
            "message": str(e),
            "status": 0
        }), 404
    except Exception as e:
        return jsonify({
            "data": [],
            "message": f"Error al eliminar la tarjeta: {str(e)}",
            "status": 0
        }), 500
