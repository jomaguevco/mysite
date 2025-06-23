import pymysql

def obtener_conexion():
    return pymysql.connect(host='memoriescity.mysql.pythonanywhere-services.com',
                           user='memoriescity',
                           password='jalados2025',
                           db='memoriescity$VINILVIBES')

# Alias for obtener_conexion
get_db_connection = obtener_conexion