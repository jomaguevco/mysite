from flask import Blueprint, render_template, redirect, url_for, flash, request, session, g, jsonify,make_response
from ..usuarios import control_usuario
from flask_login import login_user, logout_user, login_required
from .forms_auth import LoginForm, RegistroForm
from .control_auth import authenticate_user, register_user
from ..models import User
import pymysql
from ..bd_seguridad import get_db_connection_seguridad
from app import csrf
from flask_jwt_extended import create_access_token,unset_jwt_cookies
from flask import make_response
from flask_jwt_extended import set_access_cookies

import hashlib

import pymysql
from pymysql.cursors import DictCursor


bp = Blueprint('auth', __name__)

def encstringsha256(cadena_legible):
    h = hashlib.new('sha256')
    h.update(bytes(cadena_legible, encoding='utf-8'))
    epassword = h.hexdigest()
    return epassword

@bp.route('/get_token', methods=['POST'])
@csrf.exempt
def get_token():
    # Obtener los datos del formulario
    data = request.get_json()  # Obtener la solicitud en formato JSON
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"msg": "Faltan parámetros: email o password"}), 400

    # Autenticación del usuario con los datos proporcionados
    user_data = authenticate_user(email, password)

    if user_data:
        user = User(user_data)
        if user.is_active:
            # Crear un access token
            access_token = create_access_token(identity=str(user.id))
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"msg": "El usuario no está activo"}), 400
    else:
        return jsonify({"msg": "Correo electrónico o contraseña incorrectos"}), 401

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user_data = authenticate_user(email, password)

        if user_data:
            user = User(user_data)
            if user.is_active:
                # Inicia sesión con Flask-Login
                login_user(user)
                session['user_image'] = user.image
                session['user_id'] = user.id

                # 🟡 Generar y guardar token JWT en cookie
                access_token = create_access_token(identity=str(user.id))
                conn = get_db_connection_seguridad()
                with conn.cursor() as cursor:
                    cursor.execute("UPDATE USUARIO SET jwt_token = %s WHERE ID_USUARIO = %s", (access_token, user.id))
                conn.commit()
                conn.close()

                response = make_response(redirect(url_for('home.index')))
                set_access_cookies(response, access_token)

                return response

        flash('Correo electrónico o contraseña inválidos', 'error')

    return render_template('auth/iniciarSesion.html', form=form)


@bp.route('/logout')
def logout():
    # 1. Cierra sesión de Flask-Login (elimina current_user)
    logout_user()

    # 2. Limpia variables de sesión manuales (opcional, si las usas)
    session.pop('user_image', None)
    session.pop('user_id', None)

    # 3. Prepara respuesta y elimina cookie JWT del navegador
    response = make_response(redirect(url_for('home.index')))
    unset_jwt_cookies(response)

    # 4. Elimina el token JWT de la BD por seguridad
    conn = get_db_connection_seguridad()
    with conn.cursor() as cursor:
        cursor.execute("UPDATE USUARIO SET jwt_token = NULL WHERE jwt_token IS NOT NULL")
    conn.commit()
    conn.close()

    return response



@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistroForm()
    if form.validate_on_submit():
        if register_user(form.data):
            flash('Registro exitoso. Por favor, inicia sesión.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Error en el registro. Por favor, intenta de nuevo.', 'error')
    return render_template('auth/crearCuenta.html', form=form)
