from flask import Blueprint, render_template, redirect

main_bp = Blueprint("main", __name__, template_folder="templates")

@main_bp.route("/")
def index():
    return render_template('bienvenida.html')

@main_bp.route("/home")
def bienvenida():
    return render_template('home.html')


@main_bp.route("/nosotros")
def nosotros():
    return render_template('about.html')

@main_bp.route('/Bienvenido/<nombre>')
def Bienvenida_nombre(nombre):
    return f'!Bienvenid@, {nombre}'

