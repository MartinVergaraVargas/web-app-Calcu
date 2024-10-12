from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# Clase Usuario
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido1 = db.Column(db.String(100), nullable=False)
    apellido2 = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    contraseña = db.Column(db.String(200), nullable=False)
    
    # Relación con Favorito
    favoritos = db.relationship('Favorito', backref='usuario', lazy=True)
    
    # Relación con UsuarioStock
    stock_reports = db.relationship('UsuarioStock', backref='usuario', lazy=True)

# Clase Empresa
class Empresa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    numero_telefonico = db.Column(db.String(20), nullable=True)
    sitio_web = db.Column(db.String(100), nullable=True)
    contraseña = db.Column(db.String(200), nullable=False)
    rubro = db.Column(db.String(100), nullable=False)
    
    # Relación con Ubicación y Oferta
    ubicaciones = db.relationship('Ubicacion', backref='empresa', lazy=True)
    ofertas = db.relationship('Oferta', backref='empresa', lazy=True)

# Clase Ubicacion
class Ubicacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    
    # Denota si la ubicación es propia de la empresa o no
    es_propia = db.Column(db.Boolean, default=False)
    
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    
    # Relación con UbicacionOferta
    ubicacion_ofertas = db.relationship('UbicacionOferta', backref='ubicacion', lazy=True)

# Clase Oferta
class Oferta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # Servicio, Descuento o Producto
    porcentaje_descuento = db.Column(db.Float, nullable=True)  # Puede no ser necesario
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=False)
    
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    
    # Relación con UbicacionOferta
    ubicacion_ofertas = db.relationship('UbicacionOferta', backref='oferta', lazy=True)

# Clase UbicacionOferta (tabla intermedia entre Ubicación y Oferta)
class UbicacionOferta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicacion.id'), nullable=False)
    oferta_id = db.Column(db.Integer, db.ForeignKey('oferta.id'), nullable=False)
    
    # Relación con Stock
    stocks = db.relationship('Stock', backref='ubicacion_oferta', lazy=True)

# Clase Favorito (relación entre Usuario y Oferta)
class Favorito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    oferta_id = db.Column(db.Integer, db.ForeignKey('oferta.id'), nullable=False)

# Clase Stock (relaciona una oferta en una ubicación con su stock)
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ubicacion_oferta_id = db.Column(db.Integer, db.ForeignKey('ubicacion_oferta.id'), nullable=False)
    
    estado = db.Column(db.Boolean, nullable=False)  # True = hay stock, False = no hay stock
    fecha_actualizacion = db.Column(db.DateTime, nullable=False)
    es_oficial = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relación con UsuarioStock
    usuarios = db.relationship('UsuarioStock', backref='stock', lazy=True)

# Clase UsuarioStock (tabla intermedia entre Usuario y Stock)
class UsuarioStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    
    estado = db.Column(db.Boolean, nullable=False)  # True = hay stock, False = no hay stock
    fecha_actualizacion = db.Column(db.DateTime, nullable=False)
