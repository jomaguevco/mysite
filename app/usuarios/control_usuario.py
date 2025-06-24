from app.bd_seguridad import get_db_connection_seguridad

def get_user(user_id):
    conn = get_db_connection_seguridad()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT ID_USUARIO, ID_ROL, NOMBRE_USUARIO, EMAIL, TELEFONO, TIPO_DOC,
                   NRO_DOCUMENTO, DIRECCION, PROVINCIA, DISTRITO, CODIGO_POSTAL,
                   APARTAMENTO, DEPARTAMENTO, ESTADO_USUARIO, NOMBRES,
                   APELLIDO_PAT, APELLIDO_MAT, FECHA_REGISTRO, URL_IMG
            FROM USUARIO
            WHERE ID_USUARIO = %s
            """
            cursor.execute(sql, (user_id,))
            user = cursor.fetchone()
            return user
    finally:
        conn.close()

def get_all_users():
    conn = get_db_connection_seguridad()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT *
            FROM USUARIO
            """
            cursor.execute(sql)
            users = cursor.fetchall()
            return users
    finally:
        conn.close()

def get_users_by_estado(estado_usuario):
    conn = get_db_connection_seguridad()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT *
            FROM USUARIO
            WHERE ESTADO_USUARIO = %s
            """
            cursor.execute(sql, (estado_usuario,))
            users = cursor.fetchall()
            return users
    finally:
        conn.close()

def insertarUsuario(user_data):
    conn = get_db_connection_seguridad()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO USUARIO (ID_ROL, NOMBRE_USUARIO, PASSWORD, EMAIL, TELEFONO, TIPO_DOC, NRO_DOCUMENTO,
                                 DIRECCION, PROVINCIA, DISTRITO, CODIGO_POSTAL, APARTAMENTO,
                                 DEPARTAMENTO, ESTADO_USUARIO, NOMBRES, APELLIDO_PAT, APELLIDO_MAT,
                                 FECHA_REGISTRO, URL_IMG)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                user_data['id_rol'],
                user_data['nombre_usuario'],
                user_data['password'],  # Ya viene encriptado
                user_data['email'],
                user_data['telefono'],
                user_data['tipo_doc'],
                user_data['nro_documento'],
                user_data['direccion'],
                user_data['provincia'],
                user_data['distrito'],
                user_data['codigo_postal'],
                user_data['apartamento'],
                user_data['departamento'],
                user_data['estado_usuario'],
                user_data['nombres'],
                user_data['apellido_pat'],
                user_data['apellido_mat'],
                user_data['fecha_registro'],
                user_data['url_img']
            ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error inserting user: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def update_user(user_id, user_data):
    conn = get_db_connection_seguridad()
    try:
        with conn.cursor() as cursor:
            # Recupera la contraseña actual si no se envía una nueva
            if not user_data.get('password'):
                cursor.execute("SELECT PASSWORD FROM USUARIO WHERE ID_USUARIO = %s", (user_id,))
                user_data['password'] = cursor.fetchone()[0]
            sql = """
            UPDATE USUARIO
            SET ID_ROL = %s, NOMBRE_USUARIO = %s, PASSWORD = %s, EMAIL = %s, TELEFONO = %s,
                TIPO_DOC = %s, NRO_DOCUMENTO = %s, DIRECCION = %s, PROVINCIA = %s, DISTRITO = %s,
                CODIGO_POSTAL = %s, APARTAMENTO = %s, DEPARTAMENTO = %s, ESTADO_USUARIO = %s,
                NOMBRES = %s, APELLIDO_PAT = %s, APELLIDO_MAT = %s, URL_IMG = %s
            WHERE ID_USUARIO = %s
            """
            cursor.execute(sql, (
                user_data['id_rol'],
                user_data['nombre_usuario'],
                user_data['password'],
                user_data['email'],
                user_data['telefono'],
                user_data['tipo_doc'],
                user_data['nro_documento'],
                user_data['direccion'],
                user_data['provincia'],
                user_data['distrito'],
                user_data['codigo_postal'],
                user_data['apartamento'],
                user_data['departamento'],
                user_data['estado_usuario'],
                user_data['nombres'],
                user_data['apellido_pat'],
                user_data['apellido_mat'],
                user_data['url_img'],
                user_id
            ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating user: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def update_user_perfil(user_id, user_data):
    conn = get_db_connection_seguridad()
    try:
        with conn.cursor() as cursor:
            # Recupera la contraseña actual si no se envía una nueva
            if not user_data.get('password'):
                cursor.execute("SELECT PASSWORD FROM USUARIO WHERE ID_USUARIO = %s", (user_id,))
                user_data['password'] = cursor.fetchone()[0]
            sql = """
            UPDATE USUARIO
            SET PASSWORD = %s, TELEFONO = %s,
                DIRECCION = %s, PROVINCIA = %s, DISTRITO = %s,
                CODIGO_POSTAL = %s, APARTAMENTO = %s, DEPARTAMENTO = %s,
                NOMBRES = %s, APELLIDO_PAT = %s, APELLIDO_MAT = %s, URL_IMG = %s
            WHERE ID_USUARIO = %s
            """
            cursor.execute(sql, (
                user_data['password'],
                user_data['telefono'],
                user_data['direccion'],
                user_data['provincia'],
                user_data['distrito'],
                user_data['codigo_postal'],
                user_data['apartamento'],
                user_data['departamento'],
                user_data['nombres'],
                user_data['apellido_pat'],
                user_data['apellido_mat'],
                user_data['url_img'],
                user_id
            ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating user: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_all_users_rol():
    conn = get_db_connection_seguridad()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT *
            FROM USUARIO
            INNER JOIN ROL ON USUARIO.ID_ROL = ROL.ID_ROL
            """
            cursor.execute(sql)
            users = cursor.fetchall()
            return users
    finally:
        conn.close()

def get_all_users_email():
    conn = get_db_connection_seguridad()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT *
            FROM USUARIO
            INNER JOIN ROL ON USUARIO.ID_ROL = ROL.ID_ROL
            """
            cursor.execute(sql)
            users = cursor.fetchall()
            return users
    finally:
        conn.close()


def get_user_by_id(user_id):
    conn = get_db_connection_seguridad()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT *
            FROM USUARIO
            LEFT JOIN ROL ON USUARIO.ID_ROL = ROL.ID_ROL
            WHERE USUARIO.ID_USUARIO = %s
            """
            cursor.execute(sql, (int(user_id),))
            user = cursor.fetchone()
            return user
    finally:
        conn.close()


def delete_user(user_id):
    conn = get_db_connection_seguridad()
    try:
        # Primero verificar si el usuario existe
        with conn.cursor() as cursor:
            check_sql = "SELECT ID_USUARIO FROM USUARIO WHERE ID_USUARIO = %s"
            cursor.execute(check_sql, (user_id,))
            if not cursor.fetchone():
                return False

        # Proceder con la eliminación
        with conn.cursor() as cursor:
            sql = "DELETE FROM USUARIO WHERE ID_USUARIO = %s"
            cursor.execute(sql, (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def obtenerUsuarioPorEmail2(email):
    conn = get_db_connection_seguridad()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT *  # Cambiado para obtener todos los campos
            FROM USUARIO
            WHERE EMAIL LIKE %s
            """
            cursor.execute(sql, (f'%{email}%',))  # Agregado LIKE para búsqueda parcial
            users = cursor.fetchall()  # Cambiado a fetchall()
            return users
    finally:
        conn.close()

def obtenerUsuarioRolPorEmail2(email):
    if not email:
        return []

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT *
            FROM USUARIO U
            INNER JOIN ROL R ON U.ID_ROL = R.ID_ROL
            WHERE U.EMAIL = %s
            """
            cursor.execute(sql, (email,))
            user = cursor.fetchone()
            return user
    finally:
        conn.close()