from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TelField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo

# Formulario de inicio de sesión
class LoginForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email(message='Correo electrónico inválido')])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6, message='La contraseña debe tener al menos 6 caracteres')])
    submit = SubmitField('Iniciar Sesión')

# Formulario de registro de cuenta
class RegistroForm(FlaskForm):
    nombres = StringField('Nombres', validators=[DataRequired(), Length(min=2, max=50, message='El nombre debe tener entre 2 y 50 caracteres')])
    apellido_pat = StringField('Apellido Paterno', validators=[DataRequired(), Length(min=2, max=50, message='El apellido debe tener entre 2 y 50 caracteres')])
    apellido_mat = StringField('Apellido Materno', validators=[Length(max=50, message='El apellido no puede tener más de 50 caracteres')])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email(message='Correo electrónico inválido')])
    direccion = TextAreaField('Dirección', validators=[DataRequired(), Length(min=10, max=200, message='La dirección debe tener entre 10 y 200 caracteres')])
    nombre_usuario = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=4, max=25, message='El nombre de usuario debe tener entre 4 y 25 caracteres')])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6, message='La contraseña debe tener al menos 6 caracteres')])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password', message='Las contraseñas no coinciden')])
    telefono = TelField('Teléfono', validators=[DataRequired(), Length(min=10, max=15, message='El número de teléfono debe tener entre 10 y 15 caracteres')])
    submit = SubmitField('Registrar Cuenta')
