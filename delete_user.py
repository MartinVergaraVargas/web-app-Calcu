# delete_user.py
from appCalcu import create_app, db
from appCalcu.models import CommonUser, Empresa, Administrador
import sys

def mostrar_usuarios(modelo, tipo):
    usuarios = modelo.query.all()
    if not usuarios:
        print(f"\nNo hay {tipo}s registrados.")
        return False
    
    print(f"\nLista de {tipo}s:")
    print("-" * 50)
    for usuario in usuarios:
        if isinstance(usuario, CommonUser):
            print(f"ID: {usuario.id} | Email: {usuario.email} | Nombre: {usuario.nombre_completo}")
        else:
            print(f"ID: {usuario.id} | Email: {usuario.email} | Nombre: {usuario.nombre}")
    print("-" * 50)
    return True

def eliminar_usuario():
    # Crear la aplicación y el contexto
    app = create_app()
    app.app_context().push()

    print("\n=== Eliminación de Usuario ===")
    print("1. Usuario Común")
    print("2. Empresa")
    print("3. Administrador")
    
    try:
        opcion = input("\nSeleccione el tipo de usuario a eliminar (1-3): ").strip()
        
        if opcion == "1":
            modelo = CommonUser
            tipo = "usuario común"
        elif opcion == "2":
            modelo = Empresa
            tipo = "empresa"
        elif opcion == "3":
            modelo = Administrador
            tipo = "administrador"
        else:
            print("❌ Opción inválida")
            return

        if not mostrar_usuarios(modelo, tipo):
            return

        id_usuario = input(f"\nIngrese el ID del {tipo} a eliminar (o 'q' para salir): ").strip()
        
        if id_usuario.lower() == 'q':
            print("\nOperación cancelada.")
            return

        try:
            id_usuario = int(id_usuario)
        except ValueError:
            print("❌ ID inválido")
            return

        usuario = modelo.query.get(id_usuario)
        if not usuario:
            print(f"❌ No se encontró {tipo} con ID {id_usuario}")
            return

        # Mostrar información del usuario y pedir confirmación
        print("\nSe eliminará el siguiente usuario:")
        print("-" * 50)
        if isinstance(usuario, CommonUser):
            print(f"ID: {usuario.id}")
            print(f"Nombre: {usuario.nombre_completo}")
        else:
            print(f"ID: {usuario.id}")
            print(f"Nombre: {usuario.nombre}")
        print(f"Email: {usuario.email}")
        print("-" * 50)

        confirmacion = input("\n¿Está seguro de eliminar este usuario? (s/N): ").strip().lower()
        
        if confirmacion == 's':
            try:
                db.session.delete(usuario)
                db.session.commit()
                print(f"\n✅ {tipo.capitalize()} eliminado exitosamente.")
            except Exception as e:
                db.session.rollback()
                print(f"\n❌ Error al eliminar: {str(e)}")
        else:
            print("\nOperación cancelada.")

    except KeyboardInterrupt:
        print("\n\nOperación cancelada por el usuario.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    eliminar_usuario()