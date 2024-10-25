from werkzeug.security import generate_password_hash
from appCalcu import create_app, db
from appCalcu.models import Administrador

app = create_app()

with app.app_context():
    email = 'admin@example.com'
    nombre = 'Admin User'
    password = 'adminpassword'

    # Check if the email already exists
    existing_admin = Administrador.query.filter_by(email=email).first()
    if existing_admin:
        print('Email address already exists')
    else:
        # Create a new Administrador
        new_admin = Administrador(
            email=email,
            nombre=nombre,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )

        db.session.add(new_admin)
        db.session.commit()

        print('Administrador account created successfully')