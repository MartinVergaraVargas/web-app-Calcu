from datetime import datetime
from enum import Enum
from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    ultima_conexion = db.Column(db.DateTime)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.email}>'

class CommonUser(User):
    __tablename__ = 'common_user'
    apellido1 = db.Column(db.String(100), nullable=False)
    apellido2 = db.Column(db.String(100))
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    telefono = db.Column(db.String(20))
    verificacion_email = db.Column(db.Boolean, default=False)
    token_verificacion = db.Column(db.String(100))  # Para el proceso de verificación por email
    
    # Relaciones
    favoritos = db.relationship('Favorito', backref='usuario', lazy=True, cascade='all, delete-orphan')
    reportes_stock = db.relationship('UsuarioStock', backref='usuario', lazy=True, cascade='all, delete-orphan')
    
    @property
    def nombre_completo(self):
        if self.apellido2:
            return f"{self.nombre} {self.apellido1} {self.apellido2}"
        return f"{self.nombre} {self.apellido1}"
    
    def get_all_favoritos(self):
        favoritos = Favorito.query.filter_by(usuario_id=self.id).all()
        ofertas = []
        for fav in favoritos:
            if fav.tipo_oferta == 'servicio':
                oferta = ServicioOferta.query.get(fav.oferta_id)
            elif fav.tipo_oferta == 'producto':
                oferta = ProductoOferta.query.get(fav.oferta_id)
            else:
                oferta = DescuentoOferta.query.get(fav.oferta_id)
            ofertas.append(oferta)
        return ofertas


class Empresa(User):
    __tablename__ = 'empresa'
    rut_empresa = db.Column(db.String(50), unique=True, nullable=False)  # Renombrado para claridad
    telefono = db.Column(db.String(20))
    sitio_web = db.Column(db.String(150))
    rubro = db.Column(db.String(150))
    descripcion = db.Column(db.Text)
    # No necesita verificación ya que es creada por el admin
    
    # Relaciones
    ubicaciones = db.relationship('Ubicacion', backref='empresa', lazy=True, cascade='all, delete-orphan')
    ofertas = db.relationship('Oferta', backref='empresa', lazy=True, cascade='all, delete-orphan')

    def get_all_ofertas(self):
        servicios = ServicioOferta.query.filter_by(empresa_id=self.id).all()
        productos = ProductoOferta.query.filter_by(empresa_id=self.id).all()
        descuentos = DescuentoOferta.query.filter_by(empresa_id=self.id).all()
        return servicios + productos + descuentos


class Administrador(User):
    __tablename__ = 'administrador'
    pass

class Oferta(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha_inicio = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fecha_fin = db.Column(db.DateTime)
    activa = db.Column(db.Boolean, default=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)

    # Relaciones
    ubicaciones = db.relationship('UbicacionOferta', backref='oferta', lazy=True, cascade='all, delete-orphan')
    usuarios_favoritos = db.relationship('CommonUser', secondary='favorito', backref=db.backref('ofertas_favoritas', lazy='dynamic'))

class ServicioOferta(Oferta):
    __tablename__ = 'servicio_oferta'
    tipo_servicio = db.Column(db.String(50), nullable=False)  # 'reparacion', 'reciclaje', etc.
    precio = db.Column(db.Float)
    duracion_estimada = db.Column(db.String(50))  # "30 minutos", "1 hora", etc.

class ProductoOferta(Oferta):
    __tablename__ = 'producto_oferta'
    marca = db.Column(db.String(100))
    categoria = db.Column(db.String(100))
    precio = db.Column(db.Float, nullable=False)
    unidad_medida = db.Column(db.String(20))  # "unidad", "kg", "litro", etc.

class DescuentoOferta(Oferta):
    __tablename__ = 'descuento_oferta'
    precio_original = db.Column(db.Float, nullable=False)
    porcentaje_descuento = db.Column(db.Float, nullable=False)
    precio_final = db.Column(db.Float, nullable=False)
    condiciones = db.Column(db.Text)  # Condiciones específicas del descuento

class UbicacionOferta(db.Model):
    __tablename__ = 'ubicacion_oferta'
    id = db.Column(db.Integer, primary_key=True)
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicacion.id'), nullable=False)
    oferta_id = db.Column(db.Integer, nullable=False)  # No podemos usar ForeignKey directamente
    tipo_oferta = db.Column(db.String(20), nullable=False)  # 'servicio', 'producto', 'descuento'
    stock_disponible = db.Column(db.Boolean, default=True)
    ultima_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)
    ultima_actualizacion_oficial = db.Column(db.DateTime)

    __table_args__ = (
        db.UniqueConstraint('ubicacion_id', 'oferta_id', 'tipo_oferta'),
    )

class Favorito(db.Model):
    __tablename__ = 'favorito'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('common_user.id'), nullable=False)
    oferta_id = db.Column(db.Integer, nullable=False)
    tipo_oferta = db.Column(db.String(20), nullable=False)
    fecha_agregado = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'oferta_id', 'tipo_oferta'),
    )

class Ubicacion(db.Model):
    __tablename__ = 'ubicacion'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)  # Nombre del local/tienda
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    es_propia = db.Column(db.Boolean, default=False)  # True si es tienda propia de la empresa
    activa = db.Column(db.Boolean, default=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    
    # Relaciones
    ofertas = db.relationship('UbicacionOferta', backref='ubicacion', lazy=True, cascade='all, delete-orphan')

class UsuarioStock(db.Model):
    __tablename__ = 'usuario_stock'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('common_user.id'), nullable=False)
    ubicacion_oferta_id = db.Column(db.Integer, db.ForeignKey('ubicacion_oferta.id'), nullable=False)
    stock_disponible = db.Column(db.Boolean, nullable=False)  # True = hay stock/espacio, False = no hay
    fecha_reporte = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)