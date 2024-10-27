from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TelField, URLField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, URL, Optional

class EmpresaProfileForm(FlaskForm):
    nombre = StringField('Nombre Empresa', validators=[DataRequired(), Length(max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    rut_empresa = StringField('RUT Empresa', validators=[DataRequired(), Length(max=50)])
    telefono = TelField('Teléfono', validators=[Optional(), Length(max=20)])
    sitio_web = URLField('Sitio Web', validators=[Optional(), URL(), Length(max=150)])
    rubro = StringField('Rubro', validators=[DataRequired(), Length(max=150)])
    descripcion = TextAreaField('Descripción')
