from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from .control_usuario import get_user, update_user, get_user_by_id, obtenerUsuarioPorEmail2, insertarUsuario, get_all_users, get_users_by_estado, delete_user
from app import csrf
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from app.auth.control_auth import encstringsha256
from app.auth.decoradores_jwt import jwt_login_required
from flask_jwt_extended import jwt_required, get_jwt_identity
bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

## INICIO APIS

@bp.route('/api_obtenerUsuariosPorId/<int:user_id>', methods=['GET'])
@csrf.exempt
@jwt_required()
def api_obtenerUsuariosPorId(user_id):
    rpta = dict()
    try:
        usuario = get_user(user_id)
        if usuario:
            usuario_serializado = {
                "id_usuario": usuario[0],
                "id_rol": usuario[1],
                "nombre_usuario": usuario[2],
                "email": usuario[3],
                "telefono": usuario[4],
                "tipo_doc": usuario[5],
                "nro_documento": usuario[6],
                "direccion": usuario[7],
                "provincia": usuario[8],
                "distrito": usuario[9],
                "codigo_postal": usuario[10],
                "apartamento": usuario[11],
                "departamento": usuario[12],
                "estado_usuario": usuario[13],
                "nombres": usuario[14],
                "apellido_pat": usuario[15],
                "apellido_mat": usuario[16],
                "fecha_registro": usuario[17],
                "url_img": usuario[18]
            }
            rpta["data"] = usuario_serializado
            rpta["message"] = "Usuario obtenido correctamente"
            rpta["status"] = 1
            return jsonify(rpta), 200
        else:
            rpta["data"] = {}
            rpta["message"] = "Usuario no encontrado"
            rpta["status"] = 0
            return jsonify(rpta), 404
    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = "Error al obtener el usuario"
        rpta["status"] = 0
        return jsonify(rpta, str(e)), 500


@bp.route('/api_obtenerUsuarios', methods=['GET'])
@csrf.exempt
@jwt_required()
def api_obtenerUsuarios():

    if current_user.is_authenticated and current_user.id_rol != 1:
        return jsonify({
            "data": [],
            "message": "No tienes permiso para acceder a esta información",
            "status": 0
        }), 403

    rpta = dict()
    try:
        usuarios = get_all_users()
        usuarios_serializados = [
            {
                "id_usuario": usuario[0],
                "id_rol": usuario[1],
                "nombre_usuario": usuario[2],
                "email": usuario[3],
                "telefono": usuario[4],
                "tipo_doc": usuario[5],
                "nro_documento": usuario[6],
                "direccion": usuario[7],
                "provincia": usuario[8],
                "distrito": usuario[9],
                "codigo_postal": usuario[10],
                "apartamento": usuario[11],
                "departamento": usuario[12],
                "estado_usuario": usuario[13],
                "nombres": usuario[14],
                "apellido_pat": usuario[15],
                "apellido_mat": usuario[16],
                "fecha_registro": usuario[17],
                "url_img": usuario[18]
            }
            for usuario in usuarios
        ]
        rpta["data"] = usuarios_serializados
        rpta["message"] = "Usuarios obtenidos correctamente"
        rpta["status"] = 1
        return jsonify(rpta), 200
    except Exception as e:
        rpta["data"] = []
        rpta["message"] = "Error al obtener los usuarios"
        rpta["status"] = 0
        return jsonify(rpta, str(e)), 500


@bp.route('/api_insertarUsuario', methods=['POST'])
@csrf.exempt
@jwt_required()
def api_insertarUsuario():
    rpta = dict()
    try:
        datos = request.get_json()
        if not datos:
            rpta["data"] = {}
            rpta["message"] = "El cuerpo de la solicitud no contiene datos"
            rpta["status"] = 0
            return jsonify(rpta), 400

        campos_obligatorios = [
            'id_rol', 'nombre_usuario', 'password', 'email', 'telefono',
            'tipo_doc', 'nro_documento', 'direccion', 'provincia',
            'distrito', 'codigo_postal', 'apartamento', 'departamento',
            'estado_usuario', 'nombres', 'apellido_pat', 'apellido_mat',
            'fecha_registro', 'url_img'
        ]

        for campo in campos_obligatorios:
            if campo not in datos:
                rpta["data"] = {}
                rpta["message"] = f"El campo {campo} es obligatorio"
                rpta["status"] = 0
                return jsonify(rpta), 400

        from werkzeug.security import generate_password_hash
        datos['password'] = generate_password_hash(datos['password'])

        resultado = insertarUsuario(datos)

        if resultado:
            rpta["data"] = {}
            rpta["message"] = "Usuario insertado con éxito"
            rpta["status"] = 1
            return jsonify(rpta), 201
        else:
            rpta["data"] = {}
            rpta["message"] = "Error al insertar el usuario"
            rpta["status"] = 0
            return jsonify(rpta), 500
    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = "Error al procesar la solicitud"
        rpta["status"] = 0
        return jsonify(rpta, str(e)), 500


@bp.route('/api_modificarUsuario', methods=['POST'])
@csrf.exempt
@jwt_required()
def api_modificarUsuario():
    rpta = dict()
    try:
        datos = request.get_json()
        if not datos:
            rpta["data"] = {}
            rpta["message"] = "El cuerpo de la solicitud no contiene datos"
            rpta["status"] = 0
            return jsonify(rpta), 400

        if 'id_usuario' not in datos:
            rpta["data"] = {}
            rpta["message"] = "El campo id_usuario es obligatorio"
            rpta["status"] = 0
            return jsonify(rpta), 400

        campos_actualizables = [
            'id_rol', 'nombre_usuario', 'password', 'email', 'telefono',
            'tipo_doc', 'nro_documento', 'direccion', 'provincia',
            'distrito', 'codigo_postal', 'apartamento', 'departamento',
            'estado_usuario', 'nombres', 'apellido_pat', 'apellido_mat',
            'url_img'
        ]

        if not any(campo in datos for campo in campos_actualizables):
            rpta["data"] = {}
            rpta["message"] = "Debe proporcionar al menos un campo para actualizar"
            rpta["status"] = 0
            return jsonify(rpta), 400

        from werkzeug.security import generate_password_hash
        if 'password' in datos:
            datos['password'] = generate_password_hash(datos['password'])

        resultado = update_user(datos['id_usuario'], datos)

        if resultado:
            rpta["data"] = {}
            rpta["message"] = f"Usuario con ID {datos['id_usuario']} modificado con éxito"
            rpta["status"] = 1
            return jsonify(rpta), 200
        else:
            rpta["data"] = {}
            rpta["message"] = f"Usuario con ID {datos['id_usuario']} no encontrado"
            rpta["status"] = 0
            return jsonify(rpta), 404
    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = "Error al procesar la solicitud"
        rpta["status"] = 0
        return jsonify(rpta, str(e)), 500


@bp.route('/api_eliminarUsuario', methods=['POST'])
@csrf.exempt
@jwt_required()
def api_eliminarUsuario():
    rpta = dict()
    try:
        datos = request.get_json()
        if not datos or 'id_usuario' not in datos:
            rpta["data"] = {}
            rpta["message"] = "El campo id_usuario es obligatorio"
            rpta["status"] = 0
            return jsonify(rpta), 400

        id_usuario = datos['id_usuario']
        resultado = delete_user(id_usuario)

        if resultado:
            rpta["data"] = {}
            rpta["message"] = f"Usuario con ID {id_usuario} eliminado con éxito"
            rpta["status"] = 1
            return jsonify(rpta), 200
        else:
            rpta["data"] = {}
            rpta["message"] = f"Usuario con ID {id_usuario} no encontrado"
            rpta["status"] = 0
            return jsonify(rpta), 404
    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = "Error al intentar eliminar el usuario"
        rpta["status"] = 0
        return jsonify(rpta, str(e)), 500


######



@csrf.exempt
@bp.route('/<int:user_id>')
@jwt_login_required
def user_detail(user_id):
    user = get_user(user_id)
    if not user:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('usuarios.list_users'))
    return render_template('usuarios/user_detail.html', user=user)


@bp.route('/eliminar/<int:user_id>', methods=['POST'])
@jwt_login_required
@csrf.exempt
def delete_user_route(user_id):
    try:
        # Verificar si el usuario existe antes de eliminarlo
        user = get_user(user_id)
        if not user:
            flash('Usuario no encontrado', 'error')
            return redirect(url_for('admin.panel_usuarios_home'))

        if delete_user(user_id):
            flash('Usuario eliminado exitosamente', 'success')
        else:
            flash('Error al eliminar el usuario', 'error')

        return redirect(url_for('admin.panel_usuarios_home'))
    except Exception as e:
        flash(f'Error al eliminar el usuario: {str(e)}', 'error')
        return redirect(url_for('admin.panel_usuarios_home'))


@csrf.exempt
@bp.route('/update/<int:user_id>', methods=['GET', 'POST'])
@jwt_login_required
def update_user_route(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('admin.panel_usuarios_home'))

    if request.method == 'POST':
        form_data = request.form

        # Obtener la imagen
        URL_IMG = request.files['url_img']
        filename = secure_filename(URL_IMG.filename)

        # Construir la ruta completa al directorio 'static/media'
        upload_path = os.path.join('/home/grupo004/mysite/app/static/media', filename)

        user_data = {
            'id_rol': form_data.get('id_rol'),
            'nombre_usuario': form_data.get('nombre_usuario'),
            'password': user[3],  # Mantener la contraseña existente por defecto
            'email': form_data.get('email'),
            'telefono': form_data.get('telefono'),
            'tipo_doc': 'DNI',
            'nro_documento': form_data.get('nro_documento'),
            'direccion': form_data.get('direccion'),
            'provincia': form_data.get('provincia'),
            'distrito': form_data.get('distrito'),
            'codigo_postal': form_data.get('codigo_postal'),
            'apartamento': form_data.get('apartamento'),
            'departamento': form_data.get('departamento'),
            'estado_usuario': form_data.get('estado_usuario'),
            'nombres': form_data.get('nombres'),
            'apellido_pat': form_data.get('apellido_pat'),
            'apellido_mat': form_data.get('apellido_mat'),
            'url_img': filename
        }

        # Si se proporcionó una nueva contraseña, hashearla
        if form_data.get('password'):
            user_data['password'] = encstringsha256(form_data.get('password'))

        try:
            # Guardar la imagen si se proporcionó una nueva
            if URL_IMG:
                os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                URL_IMG.save(upload_path)

            if update_user(user_id, user_data):
                flash('Usuario actualizado exitosamente', 'success')
                return redirect(url_for('admin.panel_usuarios_home'))
            else:
                flash('Error al actualizar el usuario', 'error')
        except Exception as e:
            flash(f'Error al actualizar el usuario: {str(e)}', 'error')

    return render_template('panel/editar_usuario.html', user=user)

# @csrf.exempt
# @bp.route('/delete/<int:user_id>', methods=['POST'])
# @jwt_login_required
# def delete_user_route(user_id):
#     if delete_user(user_id):
#         flash('Usuario dado de baja exitosamente', 'success')
#     else:
#         flash('Error al dar de baja el usuario', 'error')
#     return redirect(url_for('admin.panel_usuarios_home'))


@bp.route('/buscar', methods=['POST'])
@csrf.exempt
@jwt_login_required
def buscar_usuario_por_email():
    email = request.form.get('email', '').strip()  # Obtener email y eliminar espacios

    if not email:
        flash('Por favor ingrese un email para buscar', 'warning')
        return redirect(url_for('admin.panel_usuarios_home'))

    usuarios = obtenerUsuarioPorEmail2(email)

    if not usuarios:
        flash('No se encontró ningún usuario con ese email', 'warning')
        return redirect(url_for('admin.panel_usuarios_home'))

    return render_template('panel/usuario.html', usuarios=usuarios)

@bp.route('/clientes')
def filtro():
    estado = request.args.get('estado')

    # Consulta SQL dependiendo del estado seleccionado
    if estado is not None and estado in ["A", "I"]:
        usuarios = get_users_by_estado(estado)
    else:
        usuarios = get_all_users()

    # Renderiza la página de clientes con los datos filtrados
    return render_template('panel/usuario.html', usuarios=usuarios)


@csrf.exempt
@bp.route('/insertar', methods=['GET', 'POST'])
@jwt_login_required
def insertar_usuario():
    if request.method == 'POST':
        form_data = request.form
        fecha_actual = datetime.now()
        fecha_formateada = fecha_actual.strftime('%Y-%m-%d')

        # Obtener la imagen
        URL_IMG = request.files['URL_IMG']
        filename = secure_filename(URL_IMG.filename)
        upload_path = os.path.join('/home/grupo004/mysite/app/static/media', filename)

        # Crear el directorio si no existe
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)

        # Encriptar la contraseña usando tu función
        password_encriptada = encstringsha256(form_data.get('PASSWORD'))

        # Preparar los datos del usuario
        user_data = {
            'id_rol': form_data.get('ID_ROL'),
            'nombre_usuario': form_data.get('NOMBRE_USUARIO'),
            'password': password_encriptada,  # Usar la contraseña encriptada
            'email': form_data.get('EMAIL'),
            'telefono': form_data.get('TELEFONO'),
            'tipo_doc': 'DNI',
            'nro_documento': form_data.get('NRO_DOCUMENTO'),
            'direccion': form_data.get('DIRECCION'),
            'provincia': form_data.get('PROVINCIA'),
            'distrito': form_data.get('DISTRITO'),
            'codigo_postal': form_data.get('CODIGO_POSTAL'),
            'apartamento': form_data.get('APARTAMENTO'),
            'departamento': form_data.get('DEPARTAMENTO'),
            'estado_usuario': form_data.get('ESTADO_USUARIO'),
            'nombres': form_data.get('NOMBRES'),
            'apellido_pat': form_data.get('APELLIDO_PAT'),
            'apellido_mat': form_data.get('APELLIDO_MAT'),
            'fecha_registro': fecha_formateada,
            'url_img': filename
        }

        try:
            # Guardar la imagen
            URL_IMG.save(upload_path)

            if insertarUsuario(user_data):
                flash('Usuario insertado exitosamente', 'success')
                return redirect(url_for('admin.panel_usuarios_home'))
            else:
                flash('Error al insertar el usuario', 'error')
        except Exception as e:
            flash(f'Error al insertar el usuario: {str(e)}', 'error')

    return render_template('panel/agregar_usuario.html')