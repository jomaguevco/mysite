from flask import Flask, g
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
import pymysql
from .config import Config
from .models import User

from flask_jwt_extended import JWTManager

#from flask_socketio import SocketIO

#socketio = SocketIO(cors_allowed_origins="*")


# Inicialización de extensiones
login_manager = LoginManager()
csrf = CSRFProtect()
jwt = JWTManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    #socketio.init_app(app)
    app.config['SECRET_KEY'] = 'clave-secreta'
    app.config['JWT_SECRET_KEY'] = 'clave-super-secreta'
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.config['JWT_COOKIE_SECURE'] = False
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False


    # Inicialización de las extensiones con la app
    login_manager.init_app(app)
    csrf.init_app(app)
    jwt.init_app(app)

    # Configuración del login_manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'

    # Configuración de la conexión a MySQL
    def get_db_connection():
        return pymysql.connect(host='memoriescity.mysql.pythonanywhere-services.com',
                           user='memoriescity',
                           password='jalados2025',
                           db='memoriescity$VINILVIBES')

    # Hacer que la conexión a la base de datos esté disponible en toda la aplicación
    app.get_db_connection = get_db_connection

    # Configurar g.usuario antes de cada solicitud
    @app.before_request
    def before_request():
        g.usuario = current_user if current_user.is_authenticated else None
        if g.usuario:
            print(f"User authenticated: {g.usuario.nombre_usuario}, Role: {g.usuario.id_rol}")
        else:
            print("No user authenticated")

    # Registro de blueprints
    from .home import routes_home as home_routes
    app.register_blueprint(home_routes.bp)

    from .auth import routes_auth as auth_routes
    app.register_blueprint(auth_routes.bp, url_prefix='/auth')

    from .tienda import routes_tienda as tienda_routes
    app.register_blueprint(tienda_routes.bp, url_prefix='/tienda')

    from .comprobante import routes_comprobante as comprobante_routes
    app.register_blueprint(comprobante_routes.bp, url_prefix='/comprobante')

    from .productos import routes_productos as productos_routes
    app.register_blueprint(productos_routes.bp, url_prefix='/productos')

    from .cart import routes_carrito as carrito_routes
    app.register_blueprint(carrito_routes.bp, url_prefix='/carrito')

    from .perfil import routes_perfil as perfil_routes
    app.register_blueprint(perfil_routes.bp, url_prefix='/perfil')

    from .admin import routes_admin as admin_routes
    app.register_blueprint(admin_routes.bp, url_prefix='/admin')

    from .usuarios import routes_usuario as usuarios_routes
    app.register_blueprint(usuarios_routes.bp, url_prefix='/usuarios')

    from .genero import routes_genero as genero_routes
    app.register_blueprint(genero_routes.bp, url_prefix='/genero')

    from .descuento import routes_descuento as descuento_routes
    app.register_blueprint(descuento_routes.bp, url_prefix='/descuento')

    from .productos_tienda import routes_productos_tienda as productos_tienda_routes
    app.register_blueprint(productos_tienda_routes.bp, url_prefix='/productos_tienda')

    from .rol import routes_rol as rol_routes
    app.register_blueprint(rol_routes.bp, url_prefix='/rol')

    from .ventas import routes_ventas as ventas_routes
    app.register_blueprint(ventas_routes.bp, url_prefix='/ventas')

    from .tipo_producto import routes_tipo_producto as tipo_producto
    app.register_blueprint(tipo_producto.bp,url_prefix='/tipo_producto')

    from .tarjeta import routes_tarjeta as tarjeta_routes
    app.register_blueprint(tarjeta_routes.bp, url_prefix='/tarjeta')


    # Configuración del manejador de usuarios para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)


    return app

#__all__ = ["create_app", "socketio"]
