import os

class Config:
    # Clave secreta para JWT
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'esta-es-una-clave-secreta'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'clave-secreta-para-jwt'  # Clave para firmar tokens JWT

    # Configuración de la base de datos MySQL
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'tu_usuario_mysql'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'tu_contraseña_mysql'
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'  # O la IP del servidor MySQL
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'nombre_de_tu_base_de_datos'

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Otras configuraciones de Flask
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
