from flask_wtf import FlaskForm
from wtforms import SelectField
from .control_tienda import get_genres

class FilterForm(FlaskForm):
    tipo = SelectField('Tipo', choices=[('', 'Todos'), ('Vinilo', 'Vinilo'), ('CD', 'CD'), ('Cassette', 'Cassette')])
    genero = SelectField('Género', choices=[])

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        self.genero.choices = [('', 'Todos')] + [(str(g['ID_GENERO']), g['NOMBRE_GENERO']) for g in get_genres()]