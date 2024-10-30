from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import logging
# from .config import DATABASE_URI

# Inicializa SQLAlchemy fuera de la función para reutilización en otros módulos
db =SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configuración básica de la aplicación
    app.config['SECRET_KEY'] = 'secret-key-goes-here' #arreglar con import os, os.environ.get('SECRET_KEY')y guardarlo como variable de sistema.
    csrf = CSRFProtect(app)
    # Configuración de PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@localhost:5432/glooba_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Guardado de archivos
    app.config['UPLOAD_FOLDER'] = '/home/martin/Tesis/Desarrollo/archivos_csv'

    # Inicializa la base de datos con la app
    db.init_app(app)
    csrf.init_app(app)

    # Inicializa Migrate después de configurar la base de datos
    migrate = Migrate(app, db)


    # Configuración del LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Importa el modelo User y configura el user_loader
    from .models import CommonUser, Empresa, Administrador
    from .blueprints.auth.auth import auth_bp, GuestUser

    # Configurar logging
    logger = logging.getLogger(__name__)

    @login_manager.user_loader
    def load_user(user_id):
        logger.debug(f"Intentando cargar usuario con ID: {user_id}")
        
        # Manejar usuario invitado
        if user_id == 'guest':
            logger.debug("Cargando usuario invitado")
            return GuestUser()
        
        try:
            # El user_id ahora viene en formato "TipoUsuario:id"
            user_type, id_str = user_id.split(":")
            user_id = int(id_str)
        except (ValueError, AttributeError):
            logger.warning(f"ID de usuario inválido: {user_id}")
            return None
        
        # Cargar el usuario según su tipo
        user_classes = {
            'CommonUser': CommonUser,
            'Empresa': Empresa,
            'Administrador': Administrador
        }
        
        UserClass = user_classes.get(user_type)
        if not UserClass:
            logger.warning(f"Tipo de usuario inválido: {user_type}")
            return None
        
        user = UserClass.query.get(user_id)
        if user:
            logger.debug(f"Usuario encontrado como {user_type}: {user.email}")
            return user
        
        logger.warning(f"No se encontró ningún usuario con ID: {user_id}")
        return None



    from .blueprints.main.main import main_bp
    app.register_blueprint(main_bp, url_prefix='/')

    # from .blueprints.calculadora.calculadora import calculadora_bp
    # app.register_blueprint(calculadora_bp, url_prefix='/calculadora')

    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .blueprints.administracion.administracion import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    from .blueprints.perfil.perfil import perfil_bp
    app.register_blueprint(perfil_bp, url_prefix='/perfil')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
