from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
# from .config import DATABASE_URI

# Inicializa SQLAlchemy fuera de la función para reutilización en otros módulos
db =SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configuración básica de la aplicación
    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    csrf = CSRFProtect(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

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

    @login_manager.user_loader
    def load_user(user_id):
        if user_id == 'guest':
            return GuestUser()
        try:
            user_id = int(user_id)
        except ValueError:
            return None
        user = CommonUser.query.get(user_id)
        if user:
            return user
        user = Empresa.query.get(user_id)
        if user:
            return user
        return Administrador.query.get(user_id)

    from .blueprints.main.main import main_bp
    app.register_blueprint(main_bp, url_prefix='/')

    # from .blueprints.calculadora.calculadora import calculadora_bp
    # app.register_blueprint(calculadora_bp, url_prefix='/calculadora')

    
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .blueprints.empresa.empresa import empresa_bp
    app.register_blueprint(empresa_bp, url_prefix='/empresa')

    from .blueprints.administracion.administracion import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
