from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Email, Length

class UserUpdateForm(FlaskForm):
    nombre_usuario = StringField('Nombre de Usuario', validators=[DataRequired(), Length(max=255)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    telefono = StringField('Teléfono', validators=[DataRequired(), Length(max=15)])
    direccion = StringField('Dirección', validators=[DataRequired(), Length(max=255)])
    provincia = StringField('Provincia', validators=[DataRequired(), Length(max=255)])
    distrito = StringField('Distrito', validators=[DataRequired(), Length(max=255)])
    codigo_postal = StringField('Código Postal', validators=[DataRequired(), Length(max=255)])
    apartamento = StringField('Apartamento', validators=[Length(max=255)])
    departamento = StringField('Departamento', validators=[Length(max=255)])
    estado_usuario = SelectField('Estado', choices=[('A', 'Activo'), ('I', 'Inactivo')], validators=[DataRequired()])
    nombres = StringField('Nombres', validators=[DataRequired(), Length(max=255)])
    apellido_pat = StringField('Apellido Paterno', validators=[DataRequired(), Length(max=255)])
    apellido_mat = StringField('Apellido Materno', validators=[DataRequired(), Length(max=255)])