from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, FileField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo
from werkzeug.security import generate_password_hash
from .control_admin import get_all_products, get_product, update_product, delete_product
from .forms_admin import ProductForm
from app.auth.decoradores_jwt import jwt_login_required
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from app.notificacion.control_notificacion import obtener_historial_notificaciones
from flask import render_template, flash, redirect, url_for, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.bd_seguridad import get_db_connection_seguridad
from app.tienda.control_tienda import get_recent_sales, get_sales_count, get_total_shipments, get_total_users
from flask import Blueprint


from app import csrf

from flask_jwt_extended import jwt_required, get_jwt_identity

from app.tienda.control_tienda import (
    get_recent_sales, get_sales_count, get_total_shipments, get_total_users, cambiarEstadoCancelado, cambiarEstadoTransito, cambiarEstadoEntregado, obtenerTodosEnvios, obtenerEnvioID, insertarEnvio, modificarEnvio, eliminarEnvio
)

from app.comprobante.control_comprobante import (
    obtenerTodosComprobantes
)

from app.usuarios.control_usuario import (
    insertarUsuario, get_all_users_rol, get_all_users, get_user_by_id, obtenerUsuarioPorEmail2, update_user, delete_user
)


bp = Blueprint('admin', __name__, url_prefix='/admin')

class CancelShipmentForm(FlaskForm):
    csrf_token = HiddenField()

class agregarGenero(FlaskForm):
    csrf_token = HiddenField()

class darBajaGenero(FlaskForm):
    csrf_token = HiddenField()

class darBajaProducto(FlaskForm):
    csrf_token = HiddenField()


@bp.route('/historial_notificaciones')
@jwt_login_required
def historial_notificaciones():
    if current_user.id_rol != 1:
        flash('No tienes permiso para acceder', 'error')
        return redirect(url_for('home.index'))

    notificaciones = obtener_historial_notificaciones()
    return render_template('panel/historial_notificaciones.html', notificaciones=notificaciones)




class UserForm(FlaskForm):
    nombre_usuario = StringField('Nombre de Usuario', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    nombres = StringField('Nombres', validators=[DataRequired()])
    apellido_pat = StringField('Apellido Paterno', validators=[DataRequired()])
    apellido_mat = StringField('Apellido Materno', validators=[DataRequired()])
    id_rol = SelectField('Rol', coerce=int, validators=[DataRequired()])
    url_img = FileField('Imagen de Perfil')

class DeleteUserForm(FlaskForm):
    csrf_token = HiddenField()

# Dashboard
@bp.route('/')
@bp.route('/dashboard')
@jwt_login_required
def dashboard_index():
    if current_user.id_rol != 1:
        flash('No tienes permiso para acceder a esta página', 'error')
        return redirect(url_for('home.index'))

    ventas_recientes = get_recent_sales()
    total_ventas = get_sales_count()
    total_envios = get_total_shipments()
    total_usuarios = get_total_users()

    return render_template('panel/index.html',
                           ventas_recientes=ventas_recientes,
                           total_ventas=total_ventas,
                           total_envios=total_envios,
                           total_usuarios=total_usuarios)

# Productos
@bp.route('/products')
@jwt_login_required
def list_products():
    from app.bd_seguridad import get_db_connection
    user_id = get_jwt_identity()
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, email FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
    conn.close()

    # Aquí deberías validar el rol si lo guardas también en `users`
    # if user_data['id_rol'] != 1: ...

    products = get_all_products()
    return render_template('admin/list_products.html', products=products)


@bp.route('/product/<int:product_id>', methods=['GET', 'POST'])
@jwt_login_required
def edit_product(product_id):
    if current_user.id_rol != 1:
        flash('No tienes permiso para acceder a esta página', 'error')
        return redirect(url_for('home.index'))

    form = ProductForm()
    if request.method == 'GET':
        product = get_product(product_id)
        if product:
            form.nombre_producto.data = product['NOMBRE_PRODUCTO']
            form.descripcion.data = product['DESCRIPCION']
            form.anio_lanzamiento.data = product['ANIO_LANZAMIENTO']
            form.id_genero.data = product['ID_GENERO']
            form.id_tipo_producto.data = product['ID_TIPO_PRODUCTO']
            form.precio.data = product['PRECIO']
            form.stock.data = product['STOCK']
            form.url_img.data = product['URL_IMG']
        else:
            flash('Producto no encontrado', 'error')
            return redirect(url_for('admin.dashboard_index'))

    if form.validate_on_submit():
        if update_product(product_id, form.data):
            flash('Producto actualizado con éxito', 'success')
            return redirect(url_for('admin.list_products'))
        else:
            flash('Error al actualizar el producto', 'error')

    return render_template('admin/edit_product.html', form=form, product_id=product_id)

@bp.route('/product/delete/<int:product_id>', methods=['POST'])
@jwt_login_required
def delete_product_route(product_id):
    if current_user.id_rol != 1:
        flash('No tienes permiso para realizar esta acción', 'error')
        return redirect(url_for('home.index'))

    if delete_product(product_id):
        flash('Producto eliminado con éxito', 'success')
    else:
        flash('Error al eliminar el producto', 'error')
    return redirect(url_for('admin.list_products'))

# Usuarios
@bp.route('/panel_usuarios_home')
@jwt_login_required
def panel_usuarios_home():
    if current_user.id_rol != 1:
        flash('No tienes permiso para acceder a esta página', 'error')
        return redirect(url_for('home.index'))


    usuarios = get_all_users()
    delete_form = DeleteUserForm()
    return render_template('panel/usuario.html', usuarios=usuarios, delete_form=delete_form)

@bp.route('/panel_usuarios_añadir', methods=['GET', 'POST'])
@jwt_login_required
def panel_usuarios_añadir():
    if current_user.id_rol != 1:
        flash('No tienes permiso para acceder a esta página', 'error')
        return redirect(url_for('home.index'))

    form = UserForm()
    form.id_rol.choices = [(role['ID_ROL'], role['NOMBRE_ROL']) for role in get_all_users_rol()]

    if form.validate_on_submit():
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        form_data = form.data
        form_data['ESTADO_USUARIO'] = 'A'
        form_data['FECHA_REGISTRO'] = fecha_actual
        form_data['PASSWORD'] = generate_password_hash(form_data['password'])

        if form.url_img.data:
            file = form.url_img.data
            filename = secure_filename(file.filename)
            upload_path = os.path.join(os.getcwd(), 'proyecto_web', 'app', 'static', 'media', filename)
            file.save(upload_path)
            form_data['URL_IMG'] = filename

        insertarUsuario(**form_data)
        flash('Usuario añadido con éxito', 'success')
        return redirect(url_for('admin.panel_usuarios_home'))

    return render_template('panel/agregar_usuario.html', form=form)

@bp.route('/panel_usuarios_editar/<int:id>', methods=['GET', 'POST'])
@jwt_login_required
def panel_usuarios_editar(id):
    if current_user.id_rol != 1:
        flash('No tienes permiso para acceder a esta página', 'error')
        return redirect(url_for('home.index'))

    usuario = get_user_by_id(id)
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('admin.panel_usuarios_home'))

    form = UserForm(obj=usuario)
    form.id_rol.choices = [(role['ID_ROL'], role['NOMBRE_ROL']) for role in get_all_users_rol()]

    if form.validate_on_submit():
        form_data = form.data
        form_data['PASSWORD'] = generate_password_hash(form_data['password'])

        if form.url_img.data:
            file = form.url_img.data
            filename = secure_filename(file.filename)
            upload_path = os.path.join(os.getcwd(), 'proyecto_web', 'app', 'static', 'media', filename)
            file.save(upload_path)
            form_data['URL_IMG'] = filename

        update_user(id, **form_data)
        flash('Usuario actualizado con éxito', 'success')
        return redirect(url_for('admin.panel_usuarios_home'))

    return render_template('panel/editarUsuario.html', form=form, usuario=usuario)

@bp.route('/panel_usuarios_eliminar/<int:id>', methods=['POST'])
@jwt_login_required
def panel_usuarios_eliminar(id):
    if current_user.id_rol != 1:
        flash('No tienes permiso para realizar esta acción', 'error')
        return redirect(url_for('home.index'))

    form = DeleteUserForm()
    if form.validate_on_submit():
        delete_user(id)
        flash('Usuario eliminado con éxito', 'success')
    else:
        flash('Error al eliminar el usuario', 'error')

    return redirect(url_for('admin.panel_usuarios_home'))

@bp.route('/panel_usuarios_buscar', methods=['POST'])
def panel_usuarios_buscar():
    # Verificar si el usuario tiene el rol de administrador (id_rol == 1)
    if current_user.id_rol != 1:
        flash('No tienes permiso para acceder a esta página', 'error')
        return redirect(url_for('home.index'))

    # Obtener el email desde el formulario
    email = request.form.get('email')

    # Validar que el email no esté vacío
    if not email:
        flash('Por favor ingrese un email válido', 'warning')
        return redirect(url_for('admin.panel_usuarios_home'))

    # Buscar el usuario por email
    usuarios = obtenerUsuarioPorEmail2(email)

    # Si no se encuentra ningún usuario
    if not usuarios:
        flash(f'No se encontró ningún usuario con el email {email}', 'warning')
        return redirect(url_for('admin.panel_usuarios_home'))

    # Mostrar los usuarios encontrados
    return render_template('panel/usuario.html', usuarios=usuarios, delete_form=DeleteUserForm())



# Envíos
@bp.route('/panel_envios')
@jwt_login_required
def panel_envio():
    if current_user.id_rol != 1:
        flash('No tienes permiso para acceder a esta página', 'error')
        return redirect(url_for('home.index'))

    envios = obtenerTodosEnvios()
    form = CancelShipmentForm()
    return render_template('panel/envio.html', envios=envios, form=form)

@bp.route('/panel_envios/cancelar/<int:id_envio>', methods=['POST'])
@jwt_login_required
def cancelar_envio(id_envio):
    if current_user.id_rol != 1:
        flash('No tienes permiso para realizar esta acción', 'error')
        return redirect(url_for('admin.panel_envio'))

    form = CancelShipmentForm()
    if form.validate_on_submit():
        cambiarEstadoCancelado(id_envio)
        flash('Envío cancelado con éxito', 'success')
    else:
        flash('Error al cancelar el envío', 'error')

    return redirect(url_for('admin.panel_envio'))


@bp.route('/panel_envios/entregar/<int:id_envio>', methods=['POST'])
@jwt_login_required
def cambiar_entregado_envio(id_envio):
    if current_user.id_rol != 1:
        flash('No tienes permiso para realizar esta acción', 'error')
        return redirect(url_for('admin.panel_envio'))

    form = CancelShipmentForm()
    if form.validate_on_submit():
        cambiarEstadoEntregado(id_envio)
        flash('Estado de envío modificado con éxito', 'success')
    else:
        flash('Error al modificar el envío', 'error')

    return redirect(url_for('admin.panel_envio'))

@bp.route('/panel_envios/transito/<int:id_envio>', methods=['POST'])
@jwt_login_required
def cambiar_transito_envio(id_envio):
    if current_user.id_rol != 1:
        flash('No tienes permiso para realizar esta acción', 'error')
        return redirect(url_for('admin.panel_envio'))

    form = CancelShipmentForm()
    if form.validate_on_submit():
        cambiarEstadoTransito(id_envio)
        flash('Estado de envío modificado con éxito', 'success')
    else:
        flash('Error al modificar el envío', 'error')

    return redirect(url_for('admin.panel_envio'))
#
# INICIO API ENVIOS #
@bp.route('/api_obtener_envios', methods=['GET'])
@csrf.exempt
@jwt_required()
def api_obtener_envios():
    """Endpoint para obtener todos los envíos"""
    if current_user.is_authenticated and current_user.id_rol != 1:
        return jsonify({
            "data": [],
            "message": "No tienes permiso para acceder a esta información",
            "status": 0
        }), 403

    envios = obtenerTodosEnvios()
    print(f"Lista de envios = {envios}")

    # Convertimos los envíos en una lista serializable
    envios_serializados = [
    {
        "id": envio["ID_ENVIO"],
        "venta": envio["ID_VENTA"],
        "direccion": envio["DIRECCION_ENVIO"],
        "fecha_envio": envio["FECHA_ENVIO"],
        "fecha_entrega": envio["FECHA_ENTREGA"],
        "estado": envio["ESTADO_ENVIO"],
        "numero_seguimiento": envio["NUMERO_SEGUIMIENTO"],
        "precio": envio["PRECIO"]
    }
    for envio in envios
    ]

    return jsonify({
        "data": envios_serializados,
        "message": "Envios obtenidos correctamente",
        "status": 1
    }), 200


@bp.route('/api_obtener_envio_id', methods=['GET'])
@csrf.exempt
@jwt_required()
def api_obtener_envio_id():
    """Obtiene un envío por su ID"""
    if current_user.is_authenticated and current_user.id_rol != 1:
        return jsonify({
            "data": [],
            "message": "No tienes permiso para acceder a esta información",
            "status": 0
        }), 403

    id_envio = request.json.get("id_envio")

    envio = obtenerEnvioID(id_envio)
    if not envio:
        return jsonify({
            "data": [],
            "message": "Envío no encontrado",
            "status": 0
        }), 404

    envio_serializado = {
        "id": envio["ID_ENVIO"],
        "venta": envio["ID_VENTA"],
        "direccion": envio["DIRECCION_ENVIO"],
        "fecha_envio": envio["FECHA_ENVIO"],
        "fecha_entrega": envio["FECHA_ENTREGA"],
        "estado": envio["ESTADO_ENVIO"],
        "numero_seguimiento": envio["NUMERO_SEGUIMIENTO"],
        "precio": envio["PRECIO"]
    }
    return jsonify({
        "data": envio_serializado,
        "message": "Envío obtenido correctamente",
        "status": 1
    }), 200

@bp.route('/api_crear_envio', methods=['POST'])
@csrf.exempt
@jwt_required()
def api_crear_envio():
    """Crea un nuevo envío"""
    if current_user.is_authenticated and current_user.id_rol != 1:
        return jsonify({
            "data": [],
            "message": "No tienes permiso para realizar esta acción",
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
        id_venta = data['id_venta']
        direccion = data['direccion']
        precio = data['precio']
        insertarEnvio(id_venta, direccion, precio)
        return jsonify({
            "data": [],
            "message": "Envío creado con éxito",
            "status": 1
        }), 201
    except KeyError as e:
        return jsonify({
            "data": [],
            "message": f"Faltan datos: {str(e)}",
            "status": 0
        }), 400
    except Exception as e:
        return jsonify({
            "data": [],
            "message": f"Error al crear envío: {str(e)}",
            "status": 0
        }), 500

@bp.route('/api_modificar_envio', methods=['POST'])
@csrf.exempt
@jwt_required()
def api_modificar_envio():
    """Modifica un envío existente"""
    if current_user.is_authenticated and current_user.id_rol != 1:
        return jsonify({
            "data": [],
            "message": "No tienes permiso para realizar esta acción",
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
        id_envio = data['id_envio']
        id_venta = data['id_venta']
        direccion = data['direccion']
        fecha_envio = data['fecha_envio']
        fecha_entrega = data['fecha_entrega']
        estado = data['estado']
        numero_seguimiento = data['numero_seguimiento']
        modificarEnvio(id_venta, direccion, fecha_envio, fecha_entrega, estado, numero_seguimiento, id_envio)
        return jsonify({
            "data": [],
            "message": "Envío modificado con éxito",
            "status": 1
        }), 200
    except KeyError as e:
        return jsonify({
            "data": [],
            "message": f"Faltan datos: {str(e)}",
            "status": 0
        }), 400
    except Exception as e:
        return jsonify({
            "data": [],
            "message": f"Error al modificar el envío: {str(e)}",
            "status": 0
        }), 500

@bp.route('/api_eliminar_envio', methods=['POST'])
@csrf.exempt
@jwt_required()
def api_eliminar_envio():
    """Elimina un envío existente"""
    if current_user.is_authenticated and current_user.id_rol != 1:
        return jsonify({
            "data": [],
            "message": "No tienes permiso para realizar esta acción",
            "status": 0
        }), 403

    id_envio = request.json.get("id_envio")
    try:
        eliminarEnvio(id_envio)
        return jsonify({
            "data": [],
            "message": "Envío eliminado con éxito",
            "status": 1
        }), 200
    except Exception as e:
        return jsonify({
            "data": [],
            "message": f"Error al eliminar el envío: {str(e)}",
            "status": 0
        }), 500

# FIN API ENVIOS #



# Comprobantes
@bp.route('/panel_comprobantes')
@jwt_login_required
def panel_comprobantes():
    if current_user.id_rol != 1:
        flash('No tienes permiso para acceder a esta página', 'error')
        return redirect(url_for('home.index'))

    comprobantes = obtenerTodosComprobantes()
    form = CancelShipmentForm()
    return render_template('panel/comprobante.html', comprobantes=comprobantes, form=form)


###############


