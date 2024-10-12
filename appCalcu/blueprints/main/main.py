from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from appCalcu.models import Ubicacion
from appCalcu import db


main_bp = Blueprint("main", __name__, template_folder="templates")

@main_bp.route("/mat")
def bienvenida():
    return render_template('bienvenida.html')

@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return render_template('home.html')
    else:
        return render_template('bienvenida.html')



@main_bp.route("/nosotros")
def nosotros():
    return render_template('about.html')

# @main_bp.route('/empresa_dashboard')
# @login_required
# def empresa_dashboard():
#     return render_template('empresa_dashboard.html')

@main_bp.route('/Bienvenido/<nombre>')
def Bienvenida_nombre(nombre):
    return f'!Bienvenid@, {nombre}'

# @main_bp.route('/add_ubicacion', methods=['GET', 'POST'])
# @login_required
# def add_ubicacion():
#     if request.method == 'POST':
#         latitud = request.form.get('latitud')
#         longitud = request.form.get('longitud')
#         direccion = request.form.get('direccion')
#         es_propia = request.form.get('es_propia') == 'on'

#         new_ubicacion = Ubicacion(
#             latitud=latitud,
#             longitud=longitud,
#             direccion=direccion,
#             es_propia=es_propia,
#             empresa_id=current_user.id  # Assuming you have a foreign key to Empresa
#         )

#         db.session.add(new_ubicacion)
#         db.session.commit()
#         flash('ubicacion added successfully!', 'success')
#         return redirect(url_for('main.empresa_dashboard'))

#     return render_template('add_ubicacion.html')

# @main_bp.route('/empresa/ubicaciones')
# def empresa_ubicaciones():
#     ubicaciones = Ubicacion.query.all()  # Fetch all ubicaciones from the database
#     return render_template('empresa_ubicaciones.html', ubicaciones=ubicaciones)