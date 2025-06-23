from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField
from wtforms.validators import DataRequired, NumberRange

class ReviewForm(FlaskForm):
    rating = IntegerField('Puntuación', validators=[DataRequired(), NumberRange(min=1, max=5)])
    comment = TextAreaField('Comentario', validators=[DataRequired()])