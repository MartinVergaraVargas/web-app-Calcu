from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100), nullable=False)
    apellido1 = db.Column(db.String(100), nullable=False)
    apellido2 = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<User {self.email}>'


class Empresa(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    sitio_web = db.Column(db.String(150), nullable=True)
    rubro = db.Column(db.String(150), nullable=True)
    descripcion = db.Column(db.String(255), nullable=True)
    
    # Flask-Login required methods
    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
    
    def __repr__(self):
        return f'<Empresa {self.email}>'
    
    # Relación con Ubicación y Oferta
    ubicaciones = db.relationship('Ubicacion', backref='empresa', lazy=True)
    ofertas = db.relationship('Oferta', backref='empresa', lazy=True)

class Ubicacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    es_propia = db.Column(db.Boolean, default=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)

    # Relación con UbicacionOferta
    ubicacion_ofertas = db.relationship('UbicacionOferta', backref='ubicacion', lazy=True)

class Oferta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)                                         # Servicio, Producto o Descuento
    porcentaje_descuento = db.Column(db.Float, nullable=True)                               # Porcentaje de descuento
    precio = db.Column(db.Float, nullable=True)                                             # Precio del producto o servicio
    fecha_inicio = db.Column(db.DateTime, nullable=True)                                   # Fecha de inicio de la oferta
    fecha_fin = db.Column(db.DateTime, nullable=True)                                      # Fecha de fin de la oferta
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)

    # Relación con UbicacionOferta
    ubicacion_ofertas = db.relationship('UbicacionOferta', backref='oferta', lazy=True)

class UbicacionOferta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicacion.id'), nullable=False)
    oferta_id = db.Column(db.Integer, db.ForeignKey('oferta.id'), nullable=False)


