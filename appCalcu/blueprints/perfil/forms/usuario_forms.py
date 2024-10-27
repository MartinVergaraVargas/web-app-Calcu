from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, DateField, TelField
from wtforms.validators import DataRequired, Email, Length, Optional

class UsuarioProfileForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    apellido1 = StringField('Primer Apellido', validators=[DataRequired(), Length(max=100)])
    apellido2 = StringField('Segundo Apellido', validators=[Optional(), Length(max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[DataRequired()])
    telefono = TelField('Teléfono', validators=[Optional(), Length(max=20)])
