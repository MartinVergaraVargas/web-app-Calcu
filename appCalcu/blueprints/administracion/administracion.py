from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
# from . import admin
from datetime import datetime
from appCalcu.models import db, CommonUser, Empresa, Administrador, Ubicacion, Oferta
from flask_wtf.csrf import generate_csrf

admin_bp = Blueprint('admin', __name__, template_folder='templates')

@admin_bp.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@admin_bp.route('/admin/usuarios')
def usuarios():
    users = CommonUser.query.all()
    return render_template('manejo_de_usuarios/usuarios.html', users=users)

@admin_bp.route('/admin/usuarios/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form.get('name')
        apellido1 = request.form.get('apellido1')
        apellido2 = request.form.get('apellido2')
        fecha_nacimiento = datetime.strptime(request.form.get('fecha_nacimiento'), '%Y-%m-%d')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the email already exists
        existing_user = CommonUser.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already exists')
            return redirect(url_for('admin.add_user'))

        # Create a new CommonUser
        new_user = CommonUser(
            name=name,
            apellido1=apellido1,
            apellido2=apellido2,
            fecha_nacimiento=fecha_nacimiento,
            telefono=telefono,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Common user added successfully')
        return redirect(url_for('admin.usuarios'))

    return render_template('manejo_de_usuarios/add_user.html')

@admin_bp.route('/admin/usuarios/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = CommonUser.query.get(user_id)
    if not user:
        flash('User not found')
        return redirect(url_for('admin.usuarios'))

    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        if request.form.get('password'):
            user.password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256')

        db.session.commit()

        flash('User updated successfully')
        return redirect(url_for('admin.usuarios'))

    return render_template('manejo_de_usuarios/edit_user.html', user=user)

@admin_bp.route('/admin/usuarios/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = CommonUser.query.get(user_id)
    if not user:
        flash('User not found')
        return redirect(url_for('admin.usuarios'))

    db.session.delete(user)
    db.session.commit()

    flash('User deleted successfully')
    return redirect(url_for('admin.usuarios'))

@admin_bp.route('/admin/empresas')
@login_required
def empresas():
    empresas = Empresa.query.all()
    return render_template('manejo_de_empresas/gestionar_empresas.html', empresas=empresas)

@admin_bp.route('/registrar_empresa', methods=['GET', 'POST'])
@login_required
def registrar_empresa():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        rut_empresa = request.form.get('rut_empresa')
        sitio_web = request.form.get('sitio_web')
        rubro = request.form.get('rubro')
        descripcion = request.form.get('descripcion')
        password = request.form.get('password')
        # Verificar si el email o rut_empresa ya existen
        if Empresa.query.filter_by(email=request.form.get('email')).first():
            flash('El email ya está registrado', 'error')
            return redirect(url_for('admin.registrar_empresa'))
        
        if Empresa.query.filter_by(rut_empresa=request.form.get('rut_empresa')).first():
            flash('El RUT ya está registrado', 'error')
            return redirect(url_for('admin.registrar_empresa'))

        # Create a new Empresa
        new_user = Empresa(
            nombre=nombre,
            telefono=telefono,
            email=email,
            rubro=rubro,
            descripcion=descripcion,
            rut_empresa=rut_empresa,
            sitio_web=sitio_web,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
        )
 
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Empresa registrada exitosamente', 'success')
            return redirect(url_for('admin.empresas'))
        except Exception as e:
            db.session.rollback()
            flash('Error al registrar la empresa', 'error')
            print(e)  # para debugging
            
    return render_template('manejo_de_empresas/registrar_empresa.html', csrf_token=generate_csrf())


@admin_bp.route('/eliminar_empresa/<int:id>', methods=['DELETE'])
@login_required
def eliminar_empresa(id):
    empresa = Empresa.query.get_or_404(id)
    try:
        db.session.delete(empresa)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})



@admin_bp.route('/admin/ofertas')
def ofertas():
    return render_template('manejo_de_empresas/ofertas.html')

@admin_bp.route('/admin/ubicaciones')
def ubicaciones():
    return render_template('manejo_de_empresas/ubicaciones.html')

@admin_bp.route('/admin/ubicaciones/add', methods=['GET', 'POST'])
def add_ubicacion():
    if request.method == 'POST':
        address = request.form.get('address')
        city = request.form.get('city')
        region = request.form.get('region')
        country = request.form.get('country')

        new_ubicacion = Ubicacion(address=address, city=city, region=region, country=country)
        db.session.add(new_ubicacion)
        db.session.commit()

        flash('Ubicacion added successfully')
        return redirect(url_for('admin.ubicaciones'))

    return render_template('manejo_de_empresas/add_ubicacion.html')

@admin_bp.route('/admin/ubicaciones/edit/<int:ubicacion_id>', methods=['GET', 'POST'])
def edit_ubicacion(ubicacion_id):
    ubicacion = Ubicacion.query.get(ubicacion_id)
    if not ubicacion:
        flash('Ubicacion not found')
        return redirect(url_for('admin.ubicaciones'))

    if request.method == 'POST':
        ubicacion.address = request.form.get('address')
        ubicacion.city = request.form.get('city')
        ubicacion.region = request.form.get('region')
        ubicacion.country = request.form.get('country')

        db.session.commit()

        flash('Ubicacion updated successfully')
        return redirect(url_for('admin.ubicaciones'))

    return render_template('manejo_de_empresas/edit_ubicacion.html', ubicacion=ubicacion)

@admin_bp.route('/admin/ubicaciones/delete/<int:ubicacion_id>', methods=['POST'])
def delete_ubicacion(ubicacion_id):
    ubicacion = Ubicacion.query.get(ubicacion_id)
    if not ubicacion:
        flash('Ubicacion not found')
        return redirect(url_for('admin.ubicaciones'))

    db.session.delete(ubicacion)
    db.session.commit()

    flash('Ubicacion deleted successfully')
    return redirect(url_for('admin.ubicaciones'))


# Routes for Ofertas
@admin_bp.route('/admin/ofertas/add', methods=['GET', 'POST'])
def add_oferta():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')

        new_oferta = Oferta(title=title, description=description, price=price)
        db.session.add(new_oferta)
        db.session.commit()

        flash('Oferta added successfully')
        return redirect(url_for('admin.ofertas'))

    return render_template('manejo_de_empresas/add_oferta.html')

@admin_bp.route('/admin/ofertas/edit/<int:oferta_id>', methods=['GET', 'POST'])
def edit_oferta(oferta_id):
    oferta = Oferta.query.get(oferta_id)
    if not oferta:
        flash('Oferta not found')
        return redirect(url_for('admin.ofertas'))

    if request.method == 'POST':
        oferta.title = request.form.get('title')
        oferta.description = request.form.get('description')
        oferta.price = request.form.get('price')

        db.session.commit()

        flash('Oferta updated successfully')
        return redirect(url_for('admin.ofertas'))

    return render_template('manejo_de_empresas/edit_oferta.html', oferta=oferta)

@admin_bp.route('/admin/ofertas/delete/<int:oferta_id>', methods=['POST'])
def delete_oferta(oferta_id):
    oferta = Oferta.query.get(oferta_id)
    if not oferta:
        flash('Oferta not found')
        return redirect(url_for('admin.ofertas'))

    db.session.delete(oferta)
    db.session.commit()

    flash('Oferta deleted successfully')
    return redirect(url_for('admin.ofertas'))