from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, TelField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from datetime import datetime, timedelta


class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    apellido1 = StringField('Primer Apellido', validators=[DataRequired(), Length(min=2, max=100)])
    apellido2 = StringField('Segundo Apellido', validators=[Length(max=100)])
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[DataRequired()])
    telefono = TelField('Teléfono')
    password = PasswordField('Contraseña', validators=[
        DataRequired(),
        Length(min=8, message='La contraseña debe tener al menos 8 caracteres')
    ])
    password_confirm = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(),
        EqualTo('password', message='Las contraseñas deben coincidir')
    ])

class LogInForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[
        DataRequired(),
        Length(min=8, message='La contraseña debe tener al menos 8 caracteres')
    ])
    remember = BooleanField('Recuérdame')
