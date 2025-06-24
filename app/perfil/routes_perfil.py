from flask import Blueprint, render_template, redirect, url_for, flash, request, g
from flask_login import login_required, current_user
from .control_perfil import get_user_orders, get_user_profile, get_user_orders_producto, get_user_comprobante_by_venta
from .forms_perfil import ProfileUpdateForm
from ..usuarios import control_usuario
from app import csrf
from datetime import datetime
from app.auth.decoradores_jwt import jwt_login_required
import os
from werkzeug.utils import secure_filename

bp = Blueprint('perfil', __name__, url_prefix='/perfil')

# @csrf.exempt
@bp.route('/datosPerfil')
# @jwt_login_required
def datosPerfil():
    profil = get_user_profile(current_user.get_id())
    return render_template('datosPerfil.html', profil=profil)



@csrf.exempt
@bp.route('/update', methods=['GET', 'POST'])
@jwt_login_required
def update_user_route2():
    profile = control_usuario.get_user_by_id(current_user.get_id())
    if not profile:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('perfil.datosPerfil'))

    if request.method == 'POST':
        form_data = request.form

        # Obtener la imagen
        URL_IMG = request.files['url_img']
        filename = secure_filename(URL_IMG.filename)

        # Construir la ruta completa al directorio 'static/media'
        upload_path = os.path.join(os.getcwd(), 'proyecto_web_2', 'app', 'static', 'media', filename)


        user_data = {
            'password': form_data.get('password'),
            'telefono': form_data.get('telefono'),
            'direccion': form_data.get('direccion'),
            'provincia': form_data.get('provincia'),
            'distrito': form_data.get('distrito'),
            'codigo_postal': form_data.get('codigo_postal'),
            'apartamento': form_data.get('apartamento'),
            'departamento': form_data.get('departamento'),
            'nombres': form_data.get('nombres'),
            'apellido_pat': form_data.get('apellido_pat'),
            'apellido_mat': form_data.get('apellido_mat'),
            'url_img': filename
        }

        # Guardar la imagen en la carpeta 'static/media'
        # URL_IMG.save(upload_path)

        if control_usuario.update_user_perfil(current_user.get_id(), user_data):
            flash('Usuario actualizado exitosamente', 'success')
            return redirect(url_for('perfil.datosPerfil'))
        else:
            flash('Error al actualizar el usuario', 'error')

    return render_template('miCuentaConfiguracion.html', profile=profile)


@csrf.exempt
@bp.route('/order/<int:order_id>')
@jwt_login_required
def view_order(order_id):
    # Implement order details view
    return render_template('perfil/view_order.html', order_id=order_id)

@csrf.exempt
@bp.route('/configuracion')
@jwt_login_required
def mi_configuracion():
    profile = get_user_profile(current_user.get_id())
    return render_template('miCuentaConfiguracion.html', profile=profile)

@csrf.exempt
@bp.route('/compras')
@jwt_login_required
def mis_compras():
    orders = get_user_orders(current_user.get_id())
    return render_template('miCuentaCompras.html', orders=orders)

# @csrf.exempt
@bp.route('/detalle_compra')
@jwt_login_required
def detalle_compra():
    # Obtener los parámetros de la URL
    venta_id = request.args.get('venta_id')
    producto_id = request.args.get('producto_id')

    # Llamar a la función que obtiene los detalles de la compra
    orders = get_user_orders_producto(current_user.get_id(), venta_id, producto_id)

    return render_template('detalleMisCompras.html', orders=orders)


@bp.route('/comprobante/<int:id>')
@jwt_login_required
def comprobante(id):

    comprobante = get_user_comprobante_by_venta(id)

    return render_template('comprobante.html', comprobante=comprobante)