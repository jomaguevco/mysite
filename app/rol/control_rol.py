from app.bd import obtener_conexion

def insertarRol(nombreRol):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            sql = "INSERT INTO ROL(NOMBRE_ROL, ESTADO_ROL) VALUES (%s, 'A')"
            cursor.execute(sql, (nombreRol,))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error inserting role: {e}")
        conexion.rollback()
        return False
    finally:
        conexion.close()



def set_user_rol(id_usuario, nuevo_id_rol):
    conn = obtener_conexion()
    try:
        with conn.cursor() as cursor:
            sql = """
            UPDATE USUARIO
            SET ID_ROL = %s
            WHERE ID_USUARIO = %s
            """
            cursor.execute(sql, (nuevo_id_rol, id_usuario))
            conn.commit()  # Hace que los cambios se guarden en la base de datos
            return cursor.rowcount  # Retorna el número de filas actualizadas (opcional)
    finally:
        conn.close()

def eliminarRol(idRol):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            sql = "DELETE FROM ROL WHERE ID_ROL = %s"
            cursor.execute(sql, (idRol,))
        if cursor.rowcount > 0:
            conexion.commit()
            return True
        else:
            return False
    except Exception as e:
        print(f"Error deleting role: {e}")
        conexion.rollback()
        return False
    finally:
        conexion.close()

def listarRolesTodos():
    conexion = obtener_conexion()
    roles = []
    with conexion.cursor() as cursor:
        sql = "SELECT * FROM ROL"
        cursor.execute(sql)
        roles = cursor.fetchall()
    conexion.close()
    return roles

def get_users_by_rol(id_rol):
    conn = obtener_conexion()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT *
            FROM USUARIO
            INNER JOIN ROL ON USUARIO.ID_ROL = ROL.ID_ROL
            WHERE USUARIO.ID_ROL = %s
            """
            cursor.execute(sql, (id_rol,))
            users = cursor.fetchall()
            return users
    finally:
        conn.close()

def listarRolID(idRol):
    conexion = obtener_conexion()
    rol = None
    with conexion.cursor() as cursor:
        sql = "SELECT ID_ROL, NOMBRE_ROL "
        sql += "FROM ROL WHERE ID_ROL = %s"
        cursor.execute(sql, (idRol,))
        rol = cursor.fetchone()
    conexion.close()
    return rol

def get_users_by_email(email):
    conn = obtener_conexion()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT *
            FROM USUARIO
            INNER JOIN ROL ON USUARIO.ID_ROL = ROL.ID_ROL
            WHERE USUARIO.EMAIL = %s
            """
            cursor.execute(sql, (email,))
            users = cursor.fetchall()
            return users
    finally:
        conn.close()

def update_rol(id_rol, nombre_rol):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            sql = "UPDATE ROL SET NOMBRE_ROL = %s WHERE ID_ROL = %s"
            cursor.execute(sql, (nombre_rol, id_rol))
        conexion.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error updating role: {e}")
        conexion.rollback()
        return False
    finally:
        conexion.close()