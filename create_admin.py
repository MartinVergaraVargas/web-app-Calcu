# create_admin.py
from appCalcu import create_app, db
from appCalcu.models import Administrador
from werkzeug.security import generate_password_hash
from getpass import getpass
import sys

def crear_admin():
    # Crear la aplicación y el contexto
    app = create_app()
    app.app_context().push()

    print("\n=== Creación de Usuario Administrador ===")
    print("----------------------------------------")
    
    # Solicitar datos
    try:
        nombre = input("Nombre del administrador: ").strip()
        while not nombre:
            print("El nombre es obligatorio.")
            nombre = input("Nombre del administrador: ").strip()

        email = input("Email del administrador: ").strip()
        while not email or '@' not in email:
            print("Por favor, ingrese un email válido.")
            email = input("Email del administrador: ").strip()

        # Verificar si el email ya existe
        if Administrador.query.filter_by(email=email).first():
            print("\n⚠️  Error: Ya existe un administrador con ese email.")
            sys.exit(1)

        # Solicitar y confirmar contraseña
        while True:
            password = getpass("Contraseña (mínimo 8 caracteres): ")
            if len(password) < 8:
                print("La contraseña debe tener al menos 8 caracteres.")
                continue
                
            confirm_password = getpass("Confirmar contraseña: ")
            if password != confirm_password:
                print("Las contraseñas no coinciden. Intente nuevamente.")
                continue
            
            break

        # Crear el administrador
        nuevo_admin = Administrador(
            nombre=nombre,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )

        # Guardar en la base de datos
        db.session.add(nuevo_admin)
        db.session.commit()

        print("\n✅ Administrador creado exitosamente!")
        print("----------------------------------------")
        print(f"Nombre: {nombre}")
        print(f"Email: {email}")
        print("----------------------------------------")

    except KeyboardInterrupt:
        print("\n\n❌ Proceso cancelado por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error al crear el administrador: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    crear_admin()