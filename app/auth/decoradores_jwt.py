from functools import wraps
from flask import request, redirect, url_for, flash, g, session
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.bd_seguridad import get_db_connection_seguridad
from flask_login import AnonymousUserMixin, login_user
from app.models import User

def cargar_usuario_jwt():
    user_id = get_jwt_identity()
    if not user_id:
        return AnonymousUserMixin()

    conn = get_db_connection_seguridad()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM USUARIO WHERE ID_USUARIO = %s", (user_id,))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                user_dict = dict(zip(columns, row))
                user_dict = {k.upper(): v for k, v in user_dict.items()}
                print("DEBUG:", user_dict)
                return User(user_dict)
    finally:
        conn.close()

    return AnonymousUserMixin()

def jwt_login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.method == 'OPTIONS':
            return func(*args, **kwargs)

        try:
            verify_jwt_in_request()
            token_en_cookie = request.cookies.get("access_token_cookie")
            user_id = get_jwt_identity()

            conn = get_db_connection_seguridad()
            with conn.cursor() as cursor:
                cursor.execute("SELECT jwt_token FROM USUARIO WHERE ID_USUARIO = %s", (user_id,))
                result = cursor.fetchone()
            conn.close()

            #if result[0].strip() != token_en_cookie.strip():
            #    flash("Sesión inválida", "warning")
            #    return redirect(url_for("auth.login"))

            user = cargar_usuario_jwt()
            session['user_id'] = user.id

            if user and not isinstance(user, AnonymousUserMixin):
                login_user(user, remember=False, force=True)
                g.current_user = user
            else:
                flash("Usuario inválido", "warning")
                return redirect(url_for("auth.login"))

        except Exception as e:
            print("JWT error:", str(e))
            flash("Debes iniciar sesión para acceder a esta página", "warning")
            return redirect(url_for("auth.login"))

        return func(*args, **kwargs)
    return wrapper
