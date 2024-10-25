from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, UserMixin, current_user
from appCalcu.models import CommonUser, Empresa, Administrador
from flask_wtf.csrf import generate_csrf
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, TelField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from datetime import datetime, timedelta
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
####################    Log in General    #############################################################################
class LogInForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[
        DataRequired(),
        Length(min=8, message='La contraseña debe tener al menos 8 caracteres')
    ])
    remember = BooleanField('Recuérdame')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LogInForm()
    if form.validate_on_submit():
        user = CommonUser.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            remember = True if request.form.get('remember') else False
            login_user(user, remember=remember)
            return redirect(url_for('main.index'))
        else:
            flash('Correo electrónico o contraseña incorrectos')
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