from flask import current_app

import pymysql


def insertar_notificacion(mensaje):
    try:
        conn = current_app.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO NOTIFICACION (MENSAJE) VALUES (%s)", (mensaje,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error al insertar notificación:", str(e))

def obtener_historial_notificaciones():
    conn = current_app.get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)  # <-- esto es CLAVE para que retorne como diccionario
    cursor.execute("SELECT id_notificacion, mensaje, fecha_hora, estado FROM notificacion ORDER BY fecha_hora DESC")
    notificaciones = cursor.fetchall()
    cursor.close()
    conn.close()
    return notificaciones
