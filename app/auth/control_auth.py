from app.bd_seguridad import get_db_connection_seguridad
from app.models import User
from werkzeug.security import generate_password_hash
import hashlib

def dict_fetchone(cursor):
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))

def encstringsha256(cadena_legible):
    h = hashlib.new('sha256')
    h.update(bytes(cadena_legible, encoding='utf-8'))
    epassword = h.hexdigest()
    return epassword

def dict_fetchone(cursor):
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))

def authenticate_user(email, password):
    conn = get_db_connection_seguridad()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM USUARIO WHERE EMAIL = %s AND PASSWORD = %s"
            cursor.execute(sql, (email, password))
            user_data = dict_fetchone(cursor)

            print(f"User found: {user_data}")

            if user_data:
                return user_data
            return None
    finally:
        conn.close()



def register_user(form_data):
    conn = get_db_connection_seguridad()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO USUARIO (
                NOMBRE_USUARIO, EMAIL, PASSWORD, NOMBRES, APELLIDO_PAT, APELLIDO_MAT, TELEFONO, TIPO_DOC,
                NRO_DOCUMENTO, DIRECCION, PROVINCIA, DISTRITO, CODIGO_POSTAL, APARTAMENTO,
                DEPARTAMENTO, ESTADO_USUARIO, FECHA_REGISTRO, URL_IMG, ID_ROL
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURDATE(), %s, %s)
            """
            cursor.execute(sql, (
                form_data['nombre_usuario'],
                form_data['email'],
                form_data['password'],
                form_data['nombres'],
                form_data['apellido_pat'],
                form_data['apellido_mat'],
                form_data['telefono'],
                'DNI',
                '11223399',
                'Calle default',
                'Provincia default',
                'Distrito default',
                '10000',
                'Apt 20',
                'Dept 20',
                'A',
                'user_default.jpg',
                2  # ID de rol
            ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error registering user: {e}")
        return False
    finally:
        conn.close()