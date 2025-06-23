import pymysql
from app.bd import get_db_connection

def obtener_todas_tarjetas():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT ID_TARJETA, ID_USUARIO, TIPO_TARJETA, NUMERO_TARJETA, FECHA_EXPIRACION
            FROM TARJETA
            """
            cursor.execute(sql)
            tarjetas = cursor.fetchall()

            # Convertir los resultados en una lista de diccionarios
            tarjetas_formateadas = []
            for tarjeta in tarjetas:
                tarjetas_formateadas.append({
                    "id_tarjeta": tarjeta[0],
                    "id_usuario": tarjeta[1],
                    "tipo_tarjeta": tarjeta[2],
                    "numero_tarjeta": f"**** **** **** {tarjeta[3][-4:]}",  # Ocultar parcialmente
                    "fecha_vencimiento": tarjeta[4]
                })

            return tarjetas_formateadas
    finally:
        conn.close()

def obtener_tarjeta_id(id_tarjeta):
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT ID_TARJETA, ID_USUARIO, TIPO_TARJETA, NUMERO_TARJETA, FECHA_EXPIRACION FROM TARJETA WHERE ID_TARJETA = %s"
            cursor.execute(sql, (id_tarjeta,))
            tarjeta = cursor.fetchone()
            return tarjeta
    finally:
        conn.close()

def insertar_tarjeta(id_usuario, tipo_tarjeta, numero_tarjeta, fecha_expiracion, cvv):
    """
    Inserta una tarjeta en la base de datos. Si la tarjeta ya existe, devuelve su ID.
    Si no existe, la inserta y devuelve el nuevo ID.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Verificar si ya existe la tarjeta
            check_sql = """
                SELECT ID_TARJETA
                FROM TARJETA
                WHERE ID_USUARIO = %s AND NUMERO_TARJETA = %s
            """
            cursor.execute(check_sql, (id_usuario, numero_tarjeta))
            existing_tarjeta = cursor.fetchone()

            if existing_tarjeta:
                # Si ya existe, devolver el ID existente
                return existing_tarjeta[0]

            # Insertar nueva tarjeta
            insert_sql = """
                INSERT INTO TARJETA
                (ID_USUARIO, TIPO_TARJETA, NUMERO_TARJETA, FECHA_EXPIRACION, CVV, ESTADO_TARJETA)
                VALUES (%s, %s, %s, %s, %s, 'A')
            """
            cursor.execute(insert_sql, (id_usuario, tipo_tarjeta, numero_tarjeta, fecha_expiracion, cvv))

            # Obtener el ID de la última fila insertada
            new_id = cursor.lastrowid
            conn.commit()
            return new_id
    except Exception as e:
        print(f"Error al insertar la tarjeta: {e}")
        conn.rollback()
        raise  # Lanza la excepción para que pueda ser manejada en un nivel superior
    finally:
        conn.close()


def modificar_tarjeta(id_tarjeta, tipo_tarjeta=None, numero_tarjeta=None, fecha_expiracion=None, cvv=None):
    """
    Modifica los datos de una tarjeta existente en la base de datos.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Construir la consulta dinámicamente según los campos proporcionados
            update_fields = []
            values = []

            if tipo_tarjeta:
                update_fields.append("TIPO_TARJETA = %s")
                values.append(tipo_tarjeta)
            if numero_tarjeta:
                update_fields.append("NUMERO_TARJETA = %s")
                values.append(numero_tarjeta)
            if fecha_expiracion:
                update_fields.append("FECHA_EXPIRACION = %s")
                values.append(fecha_expiracion)
            if cvv:
                update_fields.append("CVV = %s")
                values.append(cvv)

            if not update_fields:
                raise ValueError("No hay datos para actualizar")

            values.append(id_tarjeta)

            update_sql = f"""
                UPDATE TARJETA
                SET {', '.join(update_fields)}
                WHERE ID_TARJETA = %s
            """
            cursor.execute(update_sql, values)
            conn.commit()

            if cursor.rowcount == 0:
                raise ValueError("No se encontró la tarjeta especificada")
    except Exception as e:
        print(f"Error al modificar la tarjeta: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def eliminar_tarjeta(id_tarjeta):
    """
    Elimina (desactiva) una tarjeta existente en la base de datos cambiando su estado a 'I'.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            delete_sql = """
                UPDATE TARJETA
                SET ESTADO_TARJETA = 'I'
                WHERE ID_TARJETA = %s
            """
            cursor.execute(delete_sql, (id_tarjeta,))
            conn.commit()

            if cursor.rowcount == 0:
                raise ValueError("No se encontró la tarjeta especificada")
    except Exception as e:
        print(f"Error al eliminar la tarjeta: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()
