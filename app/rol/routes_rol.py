from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from .control_rol import insertarRol, eliminarRol, get_users_by_rol, set_user_rol, get_users_by_email, listarRolID, listarRolesTodos, update_rol
from ..usuarios import control_usuario
from app import csrf
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('rol', __name__, url_prefix='/rol')

## INICIO APIS - ROL

@csrf.exempt
@bp.route("/agregar")
def agregar():
    return render_template("panel/agregar_rol.html")


@csrf.exempt
@bp.route("/guardar_rol", methods=["POST"])
def guardar_rol():
    try:
        # Obtener datos del formulario
        nombre_rol = request.form["nombre_rol"]

        # Llamar a la función del controlador para insertar el rol
        insertarRol(nombre_rol)

        # Mensaje de éxito
        flash("El rol se guardó correctamente.", "success")

        # Redirigir al panel de roles
        return redirect(url_for('rol.panel_rol_home'))
    except Exception as e:
        # Mensaje de error en caso de fallo
        flash(f"Error al guardar el rol: {str(e)}", "danger")
        return redirect(url_for('rol.panel_rol_home'))


@bp.route('/api_insertarRol', methods=['POST'])
@csrf.exempt
@jwt_required()
def api_insertarRol():
    """Crea un nuevo rol"""
    try:
        datos = request.get_json()
        if not datos or 'nombre_rol' not in datos:
            return jsonify({'data': [], 'message': 'El campo nombre_rol es obligatorio', 'status': 0}), 400

        resultado = insertarRol(datos['nombre_rol'])
        if resultado:
            return jsonify({'data': [], 'message': 'Rol insertado con éxito', 'status': 1}), 201
        else:
            return jsonify({'data': [], 'message': 'Error al insertar el rol', 'status': 0}), 500
    except Exception as e:
        return jsonify({'data': [], 'message': f'Error al intentar insertar el rol: {str(e)}', 'status': 0}), 500


# API MODIFICAR ROL
@bp.route('/api_modificarRol', methods=['POST'])
@csrf.exempt
@jwt_required()
def api_modificarRol():
    """Modifica un rol existente"""
    try:
        datos = request.get_json()
        if not datos:
            return jsonify({'data': [], 'message': 'El cuerpo de la solicitud no contiene datos', 'status': 0}), 400
        if 'id_rol' not in datos or 'nombre_rol' not in datos:
            return jsonify({'data': [], 'message': 'Los campos id_rol y nombre_rol son obligatorios', 'status': 0}), 400
        resultado = update_rol(datos['id_rol'], datos['nombre_rol'])
        if resultado:
            return jsonify({'data': [], 'message': f'Rol con ID {datos["id_rol"]} modificado con éxito', 'status': 1}), 200
        else:
            return jsonify({'data': [], 'message': f'Rol con ID {datos["id_rol"]} no encontrado', 'status': 0}), 404
    except Exception as e:
        return jsonify({'data': [], 'message': f'Error al intentar modificar el rol: {str(e)}', 'status': 0}), 500


# API ELIMINAR ROL
@bp.route('/api_eliminarRol', methods=['POST'])
@csrf.exempt
@jwt_required()
def api_eliminarRol():
    """Elimina un rol existente"""
    try:
        datos = request.get_json()
        if not datos or 'id_rol' not in datos:
            return jsonify({'data': [], 'message': 'El campo id_rol es obligatorio', 'status': 0}), 400
        resultado = eliminarRol(datos['id_rol'])
        if resultado:
            return jsonify({'data': [], 'message': f'Rol con ID {datos["id_rol"]} eliminado con éxito', 'status': 1}), 200
        else:
            return jsonify({'data': [], 'message': f'Rol con ID {datos["id_rol"]} no encontrado', 'status': 0}), 404
    except Exception as e:
        return jsonify({'data': [], 'message': f'Error al intentar eliminar el rol: {str(e)}', 'status': 0}), 500


# API OBTENER TODOS LOS ROLES
@bp.route('/api_obtenerRoles', methods=['GET'])
@csrf.exempt
@jwt_required()
def api_obtenerRoles():
    """Obtiene todos los roles"""
    try:
        roles = listarRolesTodos()
        roles_serializados = [
            {
                "id_rol": rol[0],
                "nombre_rol": rol[1]
            }
            for rol in roles
        ]
        return jsonify({'data': roles_serializados, 'message': 'Roles obtenidos correctamente', 'status': 1}), 200
    except Exception as e:
        return jsonify({'data': [], 'message': f'Error al intentar obtener los roles: {str(e)}', 'status': 0}), 500


# API OBTENER ROL POR ID
@bp.route('/api_obtenerRolPorId/<int:id_rol>', methods=['GET'])
@csrf.exempt
@jwt_required()
def api_obtenerRolPorId(id_rol):
    """Obtiene un rol por su ID"""
    try:
        rol = listarRolID(id_rol)
        if rol:
            rol_serializado = {
                "id_rol": rol[0],
                "nombre_rol": rol[1]
            }
            return jsonify({'data': rol_serializado, 'message': 'Rol obtenido correctamente', 'status': 1}), 200
        else:
            return jsonify({'data': [], 'message': 'Rol no encontrado', 'status': 0}), 404
    except Exception as e:
        return jsonify({'data': [], 'message': f'Error al intentar obtener el rol: {str(e)}', 'status': 0}), 500

## FIN APIS - ROL

## FIN APIS

@csrf.exempt
@bp.route('/panel_rol_home')
def panel_rol_home():
    # Listar todos los roles
    roles = control_usuario.get_all_users_rol()
    return render_template('panel/rol.html', roles=roles)


#  Función que permite buscar en el panel de usuarios con roles

@csrf.exempt
@bp.route('/panel_rol_home_buscar', methods = ['POST'])
def panel_rol_home_buscar():
    tipo = request.form.get('email3')
    roles = control_usuario.obtenerUsuarioRolPorEmail2(tipo)
    return render_template('panel/rol.html', roles=roles)


@bp.route('/roles3')
def roles3():
    estado = request.args.get('estado')

    if estado and estado in ['1', '2']:
        roles = get_users_by_rol(estado)
    else:
        roles = control_usuario.get_all_users_rol()

    return render_template('panel/rol.html', roles=roles)


@csrf.exempt
@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_rol(id):
    # Obtener el rol actual por su ID
    rol = get_users_by_rol(id)

    if request.method == 'POST':
        # Recibir los nuevos datos del formulario
        nombreRol = request.form['valor_rol']

        # Actualizar el rol en la base de datos
        set_user_rol(id, nombreRol)

        flash('Rol actualizado exitosamente', 'success')
        return redirect(url_for('rol.panel_rol_home'))

    # Si es GET, mostrar el formulario con los datos del rol actual
    return render_template('panel/editarRol.html', rol=rol)

@csrf.exempt
@bp.route('/eliminar/<int:idRol>', methods=['POST'])
def eliminar_rol(idRol):
    # Eliminar el rol de la base de datos
    eliminarRol(idRol)

    flash('Rol eliminado exitosamente', 'success')
    return redirect(url_for('rol.panel_rol_home'))



@csrf.exempt
@bp.route('/buscar', methods=['GET', 'POST'])
def buscar_rol():
    if request.method == 'POST':
        # Obtenemos la búsqueda del formulario
        busqueda = request.form['email3']

        # Llamamos a la función de búsqueda
        roles = get_users_by_email(busqueda)

        # Si no encontramos ningún rol, mostramos un mensaje de error
        if not roles:
            flash('No se encontró ningún rol con ese ID o nombre', 'error')
            return redirect(url_for('rol.panel_rol_home'))

        # Si encontramos resultados, los mostramos
        return render_template('panel/rol.html', roles=roles)

    # Si es GET, mostrar todos los roles disponibles
    roles = control_usuario.get_all_users_rol()
    return render_template('panel/rol.html', roles=roles)