from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, AnonymousUserMixin, current_user
from appCalcu.models import User, Empresa
from appCalcu import db

auth_bp = Blueprint('auth', __name__, template_folder="templates")

# Clase que representa un usuario anónimo/invitado
class GuestUser(AnonymousUserMixin):
    def __init__(self):
        self.name = "Invitado"

    @property
    def is_authenticated(self):
        return False

# Ruta para entrar como invitado
@auth_bp.route('/guest')
def login_guest():
    guest = GuestUser()
    login_user(guest, remember=False)  # No recuerda la sesión del invitado
    return redirect(url_for('main.index'))

#########################################################################################################################
####################    Log in General    #############################################################################

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        # Check if the user exists in the User model
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            print(f"Logged in as: {current_user}")  # Print the current_user object
            return redirect(url_for('main.bienvenida'))

        # Check if the user exists in the Empresa model
        empresa = Empresa.query.filter_by(email=email).first()
        if empresa and check_password_hash(empresa.password, password):
            login_user(empresa, remember=remember)
            print(f"Logged in as: {current_user}")  # Print the current_user object
            return redirect(url_for('dashboard.dashboard'))

        # If neither user nor empresa is found or password is incorrect
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    return render_template('login.html')


#########################################################################################################################
####################    Checkeo de si el usuario es empresa o no    #####################################################

@auth_bp.route('/empresa_dashboard')
@login_required
def empresa_dashboard():
    if current_user.__class__.__name__ != 'Empresa':
        flash('Acceso denegado.')
        return redirect(url_for('main.bienvenida'))
    return render_template('empresa_dashboard.html')

#########################################################################################################################
####################    Registro para usuario natural    ################################################################
@auth_bp.route('/signup')
def signup():
    return render_template('signup.html')

#####   #####   #####   #####   #####   #####   #####   #####   #####   #####   #####   #####   #####   #####   #####   #

@auth_bp.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    apellido1 = request.form.get('apellido1')
    apellido2 = request.form.get('apellido2')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email,
                    name=name,
                    apellido1=apellido1,
                    apellido2=apellido2,
                    password=generate_password_hash(password, method='pbkdf2:sha256')
    )

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('auth.login'))

#########################################################################################################################
######################    Registro para Empresa    ######################################################################

@auth_bp.route('/signup_empresa')
def signup_empresa():
    return render_template('signup_empresa.html')

#####   #####   #####   #####   #####   #####   #####   #####   #####   #####   #####   #####   #####   #####   #####   #

@auth_bp.route('/signup_empresa', methods=['POST'])
def signup_empresa_post():
    # Get form data
    rut = request.form.get('rut')
    nombre = request.form.get('nombre')
    telefono = request.form.get('telefono')
    email = request.form.get('email')
    password = request.form.get('password')
    sitio_web = request.form.get('sitio_web')
    rubro = request.form.get('rubro')
    descripcion = request.form.get('descripcion')

    # Check if Empresa already exists
    empresa = Empresa.query.filter_by(email=email).first()
    if empresa:
        flash('Email address already exists')
        return redirect(url_for('auth.signup_empresa'))

    # Check if RUT already exists
    empresa_rut = Empresa.query.filter_by(rut=rut).first()
    if empresa_rut:
        flash('RUT already exists')
        return redirect(url_for('auth.signup_empresa'))

    # Create a new Empresa
    new_empresa = Empresa(
        rut=rut,
        nombre=nombre,
        telefono=telefono,
        email=email,
        password=generate_password_hash(password, method='pbkdf2:sha256'),
        sitio_web=sitio_web,
        rubro=rubro,
        descripcion=descripcion
    )

    # Add the new Empresa to the database
    db.session.add(new_empresa)
    db.session.commit()

    return redirect(url_for('auth.login'))

#########################################################################################################################
#########################################################################################################################


@auth_bp.route('/invitado')
def guest():
    return 'hola invitado'

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))