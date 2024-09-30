# Proyecto Calcu

Este proyecto es una aplicación web de Flask que ofrece funcionalidades de autenticación, vistas personalizadas y la opción de ingresar como invitado. 

## Requisitos Previos

Antes de comenzar, asegúrate de tener lo siguiente instalado en tu sistema:

- **Python 3.8 o superior**: [Descargar e instalar Python](https://www.python.org/downloads/)
- **pip**: Administrador de paquetes de Python. Viene preinstalado con Python.
- **Git**: Para clonar el repositorio. [Descargar e instalar Git](https://git-scm.com/downloads)
- **Virtualenv**: Para crear entornos virtuales aislados. Puedes instalarlo con:
  ```bash
  pip install virtualenv

## Clonar el repositorio:
- git clone https://github.com/YOUR_GITHUB_USERNAME/REPO_NAME.git
- cd REPO_NAME

# Crear el entorno virtual
virtualenv envCalcu

# Activar el entorno virtual en Linux/macOS
source envCalcu/bin/activate

# O en Windows
.\envCalcu\Scripts\activate

# Instalar las dependencias
pip install -r requerimientos.txt

# Configurar la base de datos
flask db init
flask db migrate -m "Inicialización de la base de datos"
flask db upgrade

# Configurar variables de entorno
SECRET_KEY="tu_secreto_aqui"
SQLALCHEMY_DATABASE_URI="sqlite:///db.sqlite"  # O tu conexión de PostgreSQL
FLASK_ENV=development

# Ejecutar la app 
flask run

# Estructura del proyecto
├── appCalcu/
│   ├── blueprints/
│   │   ├── auth/
│   │   │   ├── auth.py
│   │   │   └── templates/
│   │   │       ├── login.html
│   │   │       ├── signup.html
│   │   ├── main/
│   │   │   ├── main.py
│   │   │   └── templates/
│   │   │       ├── bienvenida.html
│   │   │       ├── home.html
│   │   │       └── about.html
│   ├── models.py
│   ├── static/
│   │   ├── css/
│   │   │   ├── bienvenida.css
│   │   │   ├── estilo.css
│   │   └── images/
│   ├── templates/
│   │   ├── layout.html
│   │   └── logLayout.html
│   └── __init__.py
├── requerimientos.txt
└── README.md

