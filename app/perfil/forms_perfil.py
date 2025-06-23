from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length

class ProfileUpdateForm(FlaskForm):
    telefono = StringField('Teléfono', validators=[DataRequired(), Length(max=15)])
    direccion = StringField('Dirección', validators=[DataRequired(), Length(max=255)])
    provincia = StringField('Provincia', validators=[DataRequired(), Length(max=255)])
    distrito = StringField('Distrito', validators=[DataRequired(), Length(max=255)])
    codigo_postal = StringField('Código Postal', validators=[DataRequired(), Length(max=10)])