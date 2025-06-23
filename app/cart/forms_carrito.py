from flask_wtf import FlaskForm
from wtforms import IntegerField, HiddenField
from wtforms.validators import DataRequired, NumberRange

class AddToCartForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)], default=1)
    tipo_producto = HiddenField('Tipo Producto', validators=[DataRequired()])