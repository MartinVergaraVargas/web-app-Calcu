from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, UserMixin, current_user
from appCalcu.models import CommonUser, Empresa, Administrador
from flask_wtf.csrf import generate_csrf
from .forms.log_forms import SignupForm, LogInForm
from datetime import datetime, timedelta, timezone
from functools import wraps
from appCalcu import db

auth_bp = Blueprint('auth', __name__, template_folder="templates")

# Clase que representa un usuario anónimo/invitado
class GuestUser(UserMixin):
    def __init__(self):
        self.id = 'guest'
        self.nombre = "Invitado"
        self.email = "guest@example.com"
    @property
    def is_authenticated(self):
        return False
    @property
    def is_active(self):
        return True
    @property
    def is_anonymous(self):
        return True
    def get_id(self):
        return self.id

# Ruta para entrar como invitado
@auth_bp.route('/guest')
def login_guest():
    guest = GuestUser()
    login_user(guest, remember=False)  # No recuerda la sesión del invitado
    return redirect(url_for('main.index'), csrf_token=generate_csrf())

@auth_bp.route('/invitado')
def guest():
    return 'hola invitado'

#########################################################################################################################
####################    Sistema de logins fallidos    ###################################################################
failed_attempts = {}

def check_login_attempts(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr
        if ip in failed_attempts:
            attempts = failed_attempts[ip]
            if attempts['count'] >= 5 and datetime.now() < attempts['lockout_until']:
                remaining = (attempts['lockout_until'] - datetime.now()).seconds
                flash(f'Demasiados intentos fallidos. Por favor espere {remaining} segundos.', 'error')
                return render_template('login.html', form=LogInForm())
            elif datetime.now() > attempts['lockout_until']:
                failed_attempts.pop(ip)
        return f(*args, **kwargs)
    return decorated_function

# @auth_bp.route('/login', methods=['GET', 'POST'])
# @check_login_attempts
# def login():
#     form = LogInForm()
#     if form.validate_on_submit():
#         # ... código de autenticación ...
#         if not user or not check_password_hash(user.password, password):
#             ip = request.remote_addr
#             if ip not in failed_attempts:
#                 failed_attempts[ip] = {'count': 1, 'lockout_until': datetime.now()}
#             else:
#                 failed_attempts[ip]['count'] += 1
#                 if failed_attempts[ip]['count'] >= 5:
#                     failed_attempts[ip]['lockout_until'] = datetime.now() + timedelta(minutes=5)
#             flash('Correo electrónico o contraseña incorrectos', 'error')



#########################################################################################################################
####################    Log in General    ###############################################################################
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LogInForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = True if request.form.get('remember') else False

        # Primero intentar con CommonUser para verificar email
        user = CommonUser.query.filter_by(email=email).first()
        if user and not user.verificacion_email:
            flash('Por favor verifica tu correo electrónico antes de iniciar sesión', 'warning')
            return render_template('login.html', form=form)

        # Intentar autenticar con cada tipo de usuario
        user = None
        for UserModel in [CommonUser, Empresa, Administrador]:
            user = UserModel.query.filter_by(email=email).first()
            if user:
                if not user.activo:
                    flash('Esta cuenta está desactivada. Por favor contacte al administrador.', 'error')
                    return render_template('login.html', form=form)
                
                if check_password_hash(user.password, password):
                    # Actualizar última conexión
                    user.ultima_conexion = datetime.now(timezone.utc)
                    db.session.commit()
                    
                    login_user(user, remember=remember)
                    
                    # Redirigir según el tipo de usuario
                    if isinstance(user, CommonUser):
                        next_page = url_for('main.index')
                    elif isinstance(user, Empresa):
                        next_page = url_for('dashboard_empresa.dashboard')
                    elif isinstance(user, Administrador):
                        next_page = url_for('admin.admin_dashboard')
                    
                    # Verificar si hay una página siguiente en la URL
                    if request.args.get('next'):
                        next_page = request.args.get('next')
                        
                    flash(f'Bienvenido, {user.nombre}!', 'success')
                    return redirect(next_page)
                break

        flash('Correo electrónico o contraseña incorrectos', 'error')
            
    return render_template('login.html', form=form)


#########################################################################################################################
####################    Creación de un usuario Administrador    #####################################################

@auth_bp.route('/crear_admin', methods=['GET', 'POST'])
def crear_admin():
    if request.method == 'POST':
        email = request.form.get('email')
        nombre = request.form.get('nombre')
        password = request.form.get('password')

        # Check if the email already exists
        existing_admin = Administrador.query.filter_by(email=email).first()
        if existing_admin:
            flash('Email address already exists')
            return redirect(url_for('auth.crear_admin'))

        # Create a new Administrador
        new_admin = Administrador(
            email=email,
            nombre=nombre,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )

        db.session.add(new_admin)
        db.session.commit()

        flash('Administrador account created successfully')
        return redirect(url_for('auth.login'))

    return render_template('crear_admin.html', csrf_token=generate_csrf())

#########################################################################################################################
####################    Conversión de un usuario común a Administrador    ###############################################

@auth_bp.route('/convert_to_admin/<int:user_id>', methods=['POST'])
def convert_to_admin(user_id):
    common_user = CommonUser.query.get(user_id)
    if not common_user:
        flash('User not found')
        return redirect(url_for('main.index'))

    # Create a new Administrador with the same details
    new_admin = Administrador(
        email=common_user.email,
        nombre=common_user.nombre,
        password=common_user.password  # Assuming the password is already hashed
    )

    db.session.add(new_admin)
    db.session.delete(common_user)
    db.session.commit()

    flash('User converted to Administrador successfully')
    return redirect(url_for('main.index'))

#########################################################################################################################
####################    Registro para usuario natural    ################################################################
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    
    if form.validate_on_submit():
        # Verificar si el email ya existe
        if CommonUser.query.filter_by(email=form.email.data).first():
            flash('Email ya registrado')
            return redirect(url_for('auth.signup'))

        # Crear nuevo usuario
        nuevo_usuario = CommonUser(
            email=form.email.data,
            nombre=form.nombre.data,
            apellido1=form.apellido1.data,
            apellido2=form.apellido2.data,
            password=generate_password_hash(form.password.data, method='pbkdf2:sha256'),
            fecha_nacimiento=form.fecha_nacimiento.data,
            telefono=form.telefono.data,
            verificacion_email=False,  # Default value
            token_verificacion=None    # Default value

        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash('Registro exitoso')
        # return redirect(url_for('auth.login'))
        return redirect(url_for('main.index'))


    return render_template('signup.html', form=form)

#########################################################################################################################
#########################################################################################################################

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))