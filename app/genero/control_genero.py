from ..bd import obtener_conexion

def obtener_generos():
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM GENERO")
            generos = cursor.fetchall()
        return generos
    except Exception as e:
        print(f"Error al obtener los géneros: {e}")
        return []
    finally:
        conexion.close()

def buscar_generos_por_nombre(nombre_genero):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Realizar búsqueda insensible a mayúsculas/minúsculas con LIKE
            cursor.execute("SELECT * FROM GENERO WHERE LOWER(NOMBRE_GENERO) LIKE LOWER(%s)", (f"%{nombre_genero}%",))
            generos = cursor.fetchall()
        return generos
    except Exception as e:
        print(f"Error al buscar géneros: {e}")
        return []
    finally:
        conexion.close()

def dar_de_baja_genero(id_genero):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("UPDATE GENERO SET ESTADO_GENERO = 'I' WHERE ID_GENERO = %s", (id_genero,))
        conexion.commit()
    except Exception as e:
        conexion.rollback()
        print(f"Error al dar de baja el género: {e}")
    finally:
        conexion.close()

def obtener_genero_por_id(id_genero):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM GENERO WHERE ID_GENERO = %s", (id_genero,))
            genero = cursor.fetchone()
        return genero
    except Exception as e:
        print(f"Error al obtener el género por ID: {e}")
        return None
    finally:
        conexion.close()

def actualizar_genero(id_genero, nombre_genero, estado_genero):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "UPDATE GENERO SET NOMBRE_GENERO = %s, ESTADO_GENERO = %s WHERE ID_GENERO = %s",
                (nombre_genero, estado_genero, id_genero)
            )
        conexion.commit()
    except Exception as e:
        conexion.rollback()
        print(f"Error al actualizar el género: {e}")
        raise  # Levantamos la excepción para manejarla en el controlador
    finally:
        conexion.close()

def insertar_genero(nombre_genero, estado_genero):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "INSERT INTO GENERO (NOMBRE_GENERO, ESTADO_GENERO) VALUES (%s, %s)",
                (nombre_genero, estado_genero)
            )
        conexion.commit()
    except Exception as e:
        conexion.rollback()
        print(f"Error al insertar el género: {e}")
        raise  # Levantamos la excepción para manejarla en el controlador
    finally:
        conexion.close()

def existe_genero(nombre_genero):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM GENERO WHERE NOMBRE_GENERO = %s", (nombre_genero,))
            genero = cursor.fetchone()  # Obtener el registro completo si existe
        return genero  # Devuelve el registro o None si no existe
    except Exception as e:
        print(f"Error al verificar si existe el género: {e}")
        return None  # Devuelve None si ocurre un error
    finally:
        conexion.close()

def eliminar_genero_sin_productos(id_genero):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Verificar si el género está asociado a productos
            cursor.execute("SELECT COUNT(*) FROM PRODUCTO WHERE ID_GENERO = %s", (id_genero,))
            productos_asociados = cursor.fetchone()[0]

            # Si hay productos asociados, no se elimina
            if productos_asociados > 0:
                return False

            # Si no hay productos asociados, eliminar el género
            cursor.execute("DELETE FROM GENERO WHERE ID_GENERO = %s", (id_genero,))
            conexion.commit()

        return True
    except Exception as e:
        conexion.rollback()
        print(f"Error al eliminar el género: {e}")
        return False
    finally:
        conexion.close()
def ejecutar_consulta(consulta):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(consulta)
            resultados = cursor.fetchall()
        return resultados
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
        return []
    finally:
        conexion.close()
