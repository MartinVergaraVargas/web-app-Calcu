from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, DateTimeField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from appCalcu.models import db, Ubicacion, Oferta, UbicacionOferta

# Define the blueprint
dashboard_bp = Blueprint('dashboard', __name__, template_folder='templates')

# Define the forms
class UbicacionForm(FlaskForm):
    latitud = FloatField('Latitud', validators=[DataRequired()])
    longitud = FloatField('Longitud', validators=[DataRequired()])
    direccion = StringField('Dirección', validators=[DataRequired()])
    es_propia = BooleanField('Es Propia')
    submit = SubmitField('Agregar Ubicación')

class OfertaForm(FlaskForm):
    descripcion = StringField('Descripción', validators=[DataRequired()])
    tipo = SelectField('Tipo', choices=[('Servicio', 'Servicio'), ('Descuento', 'Descuento'), ('Producto', 'Producto')], validators=[DataRequired()])
    porcentaje_descuento = FloatField('Porcentaje de Descuento')
    precio = FloatField('Precio')
    fecha_inicio = DateTimeField('Fecha de Inicio', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    fecha_fin = DateTimeField('Fecha de Fin', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    submit = SubmitField('Agregar Oferta')

# Define the routes
@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@dashboard_bp.route('/dashboard/add_ubicaciones', methods=['GET', 'POST'])
@login_required
def add_ubicaciones():
    form = UbicacionForm()
    if form.validate_on_submit():
        latitud = form.latitud.data
        longitud = form.longitud.data
        direccion = form.direccion.data
        es_propia = form.es_propia.data

        new_ubicaciones = Ubicacion(
            latitud=latitud,
            longitud=longitud,
            direccion=direccion,
            es_propia=es_propia,
            empresa_id=current_user.id
        )

        db.session.add(new_ubicaciones)
        db.session.commit()
        flash('ubicaciones added successfully!', 'success')
        return redirect(url_for('dashboard.dashboard'))

    return render_template('add_ubicaciones.html', form=form)

@dashboard_bp.route('/dashboard/add_ofertas', methods=['GET', 'POST'])
@login_required
def add_ofertas():
    form = OfertaForm()
    if form.validate_on_submit():
        descripcion = form.descripcion.data
        tipo = form.tipo.data
        porcentaje_descuento = form.porcentaje_descuento.data
        precio = form.precio.data
        fecha_inicio = form.fecha_inicio.data
        fecha_fin = form.fecha_fin.data

        new_oferta = Oferta(
            descripcion=descripcion,
            tipo=tipo,
            porcentaje_descuento=porcentaje_descuento,
            precio=precio,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            empresa_id=current_user.id
        )

        db.session.add(new_oferta)
        db.session.commit()
        flash('Offer added successfully!', 'success')
        return redirect(url_for('dashboard.dashboard'))

    return render_template('add_ofertas.html', form=form)