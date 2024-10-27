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
    return render_template('home.html')


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

@main_bp.route('/configuracion')
def configuracion():
    return render_template('dashboard-base.html')

