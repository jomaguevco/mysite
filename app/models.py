from flask_login import UserMixin
from app.bd_seguridad import get_db_connection_seguridad

class User(UserMixin):
    def __init__(self, user_dict):
        # Flask-Login requiere que id sea string
        self.id = str(user_dict.get('ID_USUARIO') or user_dict.get('ID'))
        self.email = user_dict['EMAIL']
        self.password = user_dict['PASSWORD']
        self.nombre_usuario = user_dict['NOMBRE_USUARIO']
        self.image = user_dict.get('URL_IMG') or user_dict.get('image') or "default.png"
        self.id_rol = user_dict['ID_ROL']
        # Asegura que is_active sea booleano
        self._is_active = user_dict.get('ESTADO_USUARIO', 'A') == 'A'

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        self._is_active = bool(value)

    @staticmethod
    def get(user_id):
        conn = get_db_connection_seguridad()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM USUARIO WHERE ID_USUARIO = %s", (user_id,))
                user_data = dict_fetchone(cursor)
                if user_data:
                    return User(user_data)
        finally:
            conn.close()
        return None

def dict_fetchone(cursor):
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))