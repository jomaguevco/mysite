from ..bd import obtener_conexion
from ..bd import obtener_conexion
from datetime import date

def obtener_descuentos():
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM DESCUENTO")
            descuentos = cursor.fetchall()
        return descuentos
    except Exception as e:
        print(f"Error al obtener los descuentos: {e}")
        return []
    finally:
        conexion.close()

def buscar_descuentos_por_porcentaje(porcentaje):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM DESCUENTO WHERE PORCENTAJE = %s", (porcentaje,))
            descuentos = cursor.fetchall()
        return descuentos
    except Exception as e:
        print(f"Error al buscar descuentos por porcentaje: {e}")
        return []
    finally:
        conexion.close()

def dar_de_baja_descuento(id_descuento):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT ESTADO_DSCTO FROM DESCUENTO WHERE ID_DESCUENTO = %s", (id_descuento,))
            estado = cursor.fetchone()
            if estado and estado[0] == 'I':
                print("El descuento ya está inactivo.")
                return False

            cursor.execute("UPDATE DESCUENTO SET ESTADO_DSCTO = 'I' WHERE ID_DESCUENTO = %s", (id_descuento,))
        conexion.commit()
        return True
    except Exception as e:
        conexion.rollback()
        print(f"Error al dar de baja el descuento: {e}")
        return False
    finally:
        conexion.close()

def obtener_descuento_por_id(id_descuento):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM DESCUENTO WHERE ID_DESCUENTO = %s", (id_descuento,))
            descuento = cursor.fetchone()
        return descuento
    except Exception as e:
        print(f"Error al obtener el descuento por ID: {e}")
        return None
    finally:
        conexion.close()

def validar_fechas(fecha_inicio, fecha_fin):
    if fecha_fin <= fecha_inicio:
        print("La fecha de fin debe ser mayor que la fecha de inicio.")
        return False
    return True

def descuento_duplicado(porcentaje, fecha_inicio, fecha_fin, id_descuento=None):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Verificar si existe otro descuento con el mismo porcentaje y fechas
            query = "SELECT COUNT(*) FROM DESCUENTO WHERE PORCENTAJE = %s AND FECHA_INICIO = %s AND FECHA_FIN = %s"
            params = (porcentaje, fecha_inicio, fecha_fin)

            if id_descuento:  # Para actualización, excluimos el mismo descuento
                query += " AND ID_DESCUENTO != %s"
                params += (id_descuento,)

            cursor.execute(query, params)
            duplicado = cursor.fetchone()[0]

        return duplicado > 0
    except Exception as e:
        print(f"Error al verificar si el descuento está duplicado: {e}")
        return True
    finally:
        conexion.close()




def eliminar_descuento_sin_productos(id_descuento):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Verificar si el descuento está asociado a productos
            cursor.execute("SELECT COUNT(*) FROM PRODUCTO WHERE ID_DESCUENTO = %s", (id_descuento,))
            productos_asociados = cursor.fetchone()[0]

            if productos_asociados > 0:
                print("No se puede eliminar el descuento porque está asociado a productos.")
                return False

            # Eliminar el descuento
            cursor.execute("DELETE FROM DESCUENTO WHERE ID_DESCUENTO = %s", (id_descuento,))
            conexion.commit()
            return True
    except Exception as e:
        conexion.rollback()
        print(f"Error al eliminar el descuento: {e}")
        return False
    finally:
        conexion.close()

def obtener_descuentos_filtrados(filtro_estado_orden):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Definir consulta base
            query = "SELECT * FROM DESCUENTO WHERE 1=1"

            # Separar el valor de estado y el valor de orden
            if filtro_estado_orden in ["A", "I"]:  # Si es estado
                query += " AND ESTADO_DSCTO = %s ORDER BY PORCENTAJE ASC"
                cursor.execute(query, (filtro_estado_orden,))
            elif filtro_estado_orden in ["asc", "desc"]:  # Si es orden
                query += f" ORDER BY PORCENTAJE {filtro_estado_orden.upper()}"
                cursor.execute(query)
            else:
                cursor.execute(query)  # Si es "todos", se ejecuta sin filtro

            descuentos = cursor.fetchall()
        return descuentos
    except Exception as e:
        print(f"Error al filtrar los descuentos: {e}")
        return []
    finally:
        conexion.close()


# Insertar un nuevo descuento
def insertar_descuento(porcentaje, fecha_inicio, fecha_fin, estado):
    # Validar que la fecha de inicio no sea mayor que la fecha de fin
    if fecha_fin and not validar_fechas(fecha_inicio, fecha_fin):
        return False

    if descuento_duplicado(porcentaje, fecha_inicio, fecha_fin):
        print("Ya existe un descuento con el mismo porcentaje y fechas.")
        return False

    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "INSERT INTO DESCUENTO (PORCENTAJE, FECHA_INICIO, FECHA_FIN, ESTADO_DSCTO) VALUES (%s, %s, %s, %s)",
                (porcentaje, fecha_inicio, fecha_fin, estado)
            )
        conexion.commit()
        return True
    except Exception as e:
        conexion.rollback()
        print(f"Error al insertar el descuento: {e}")
        raise
    finally:
        conexion.close()

# Actualizar un descuento existente
def actualizar_descuento(id_descuento, porcentaje, fecha_inicio, fecha_fin, estado):
    # Validar que la fecha de inicio no sea mayor que la fecha de fin
    if fecha_fin and not validar_fechas(fecha_inicio, fecha_fin):
        return False

    if descuento_duplicado(porcentaje, fecha_inicio, fecha_fin, id_descuento):
        print("Ya existe un descuento con el mismo porcentaje y fechas.")
        return False

    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "UPDATE DESCUENTO SET PORCENTAJE = %s, FECHA_INICIO = %s, FECHA_FIN = %s, ESTADO_DSCTO = %s WHERE ID_DESCUENTO = %s",
                (porcentaje, fecha_inicio, fecha_fin, estado, id_descuento)
            )
        conexion.commit()
        return True
    except Exception as e:
        conexion.rollback()
        print(f"Error al actualizar el descuento: {e}")
        raise
    finally:
        conexion.close()

def validar_fechas(fecha_inicio, fecha_fin):
    if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
        print("La fecha de fin no puede ser anterior a la fecha de inicio.")
        return False
    return True


def obtener_todas_resenas():
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM RESENA")
            resenas = cursor.fetchall()
        return resenas
    except Exception as e:
        print(f"Error al obtener las reseñas: {e}")
        return []
    finally:
        conexion.close()

def obtener_resena_por_id(id_resena):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Consulta para obtener la reseña por ID_RESENA
            cursor.execute("SELECT * FROM RESENA WHERE ID_RESENA = %s", (id_resena,))
            resena = cursor.fetchone()  # Obtiene la primera fila que coincide
        return resena
    except Exception as e:
        print(f"Error al obtener la reseña: {e}")
        return None
    finally:
        conexion.close()

def insertar_resena(id_producto, id_usuario, puntuacion, comentario, fecha_resena, estado):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Consulta para insertar la reseña en la base de datos
            query = """
                INSERT INTO RESENA (ID_PRODUCTO, ID_USUARIO, PUNTUACION, COMENTARIO, FECHA_RESENA, ESTADO)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (id_producto, id_usuario, puntuacion, comentario, fecha_resena, estado))
            conexion.commit()  # Confirmamos la transacción
            return True
    except Exception as e:
        conexion.rollback()  # Si ocurre un error, hacemos rollback
        print(f"Error al insertar la reseña: {e}")
        return False
    finally:
        conexion.close()

def modificar_resena(id_resena, id_producto, id_usuario, puntuacion, comentario, fecha_resena, estado):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Consulta para actualizar la reseña en la base de datos
            query = """
                UPDATE RESENA
                SET ID_PRODUCTO = %s, ID_USUARIO = %s, PUNTUACION = %s, COMENTARIO = %s, FECHA_RESENA = %s, ESTADO = %s
                WHERE ID_RESENA = %s
            """
            cursor.execute(query, (id_producto, id_usuario, puntuacion, comentario, fecha_resena, estado, id_resena))
            conexion.commit()  # Confirmamos la transacción
            return True
    except Exception as e:
        conexion.rollback()  # Si ocurre un error, hacemos rollback
        print(f"Error al modificar la reseña: {e}")
        return False
    finally:
        conexion.close()

def eliminar_resena(id_resena):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Consulta para eliminar la reseña de la base de datos
            query = "DELETE FROM RESENA WHERE ID_RESENA = %s"
            cursor.execute(query, (id_resena,))
            conexion.commit()  # Confirmamos la transacción
            return True
    except Exception as e:
        conexion.rollback()  # Si ocurre un error, hacemos rollback
        print(f"Error al eliminar la reseña: {e}")
        return False
    finally:
        conexion.close()

