from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, SelectField
from wtforms.validators import DataRequired, NumberRange
from app.bd import get_db_connection

class ProductForm(FlaskForm):
    nombre_producto = StringField('Nombre del Producto', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción', validators=[DataRequired()])
    anio_lanzamiento = IntegerField('Año de Lanzamiento', validators=[DataRequired(), NumberRange(min=1900, max=2100)])
    id_genero = SelectField('Género', coerce=int, validators=[DataRequired()])
    id_tipo_producto = SelectField('Tipo de Producto', coerce=int, validators=[DataRequired()])
    precio = DecimalField('Precio', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    url_img = StringField('URL de la Imagen', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT ID_GENERO, NOMBRE_GENERO FROM GENERO")
                self.id_genero.choices = [(g['ID_GENERO'], g['NOMBRE_GENERO']) for g in cursor.fetchall()]

                cursor.execute("SELECT ID_TIPO_PRODUCTO, NOMBRE_TIPO_PRODUCTO FROM TIPO_PRODUCTO")
                self.id_tipo_producto.choices = [(t['ID_TIPO_PRODUCTO'], t['NOMBRE_TIPO_PRODUCTO']) for t in cursor.fetchall()]
        finally:
            conn.close()


