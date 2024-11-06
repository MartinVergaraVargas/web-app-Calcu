from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed

class ImportarEmpresasForm(FlaskForm):
    file = FileField('Archivo CSV', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'Solo archivos CSV!')
    ])


class ImportarOfertasForm(FlaskForm):
    file = FileField('Archivo CSV', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'Solo archivos CSV!')
    ])
