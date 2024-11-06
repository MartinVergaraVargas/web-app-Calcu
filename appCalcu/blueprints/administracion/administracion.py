import csv
from io import StringIO
import pandas as pd
import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app, send_file
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash
# from . import admin
from datetime import datetime
from appCalcu.models import db, CommonUser, Empresa, Administrador, Ubicacion, Oferta
from flask_wtf.csrf import generate_csrf

admin_bp = Blueprint('admin', __name__, template_folder='templates')

@admin_bp.route('/admin')
@login_required
def dashboard():
    return render_template('actividad_dashboard.html')

@admin_bp.route('/admin/usuarios')
@login_required
def usuarios():
    users = CommonUser.query.all()
    return render_template('manejo_de_usuarios/usuarios.html', users=users)

@admin_bp.route('/admin/usuarios/add', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
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
    form_empresas = ImportarEmpresasForm()
    form_ofertas = ImportarOfertasForm()
    return render_template('manejo_de_empresas/gestionar_empresas.html', 
                         empresas=empresas, 
                         form=form_empresas,
                         form_ofertas=form_ofertas)


@admin_bp.route('/registrar_empresa', methods=['GET', 'POST'])
@login_required
def registrar_empresa():
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.form.get('nombre')
            telefono = request.form.get('telefono')
            email = request.form.get('email')
            rut_empresa = request.form.get('rut_empresa')
            sitio_web = request.form.get('sitio_web')
            rubro = request.form.get('rubro')
            descripcion = request.form.get('descripcion')
            password = request.form.get('password')

            # Validaciones de campos requeridos
            if not all([nombre, email, rut_empresa, password]):
                flash('Los campos nombre, email, RUT y contraseña son obligatorios', 'error')
                return redirect(url_for('admin.registrar_empresa'))

            # Verificar si el email ya existe
            if Empresa.query.filter_by(email=email).first():
                flash('El email ya está registrado', 'error')
                return redirect(url_for('admin.registrar_empresa'))
            
            # Verificar si el RUT ya existe
            if Empresa.query.filter_by(rut_empresa=rut_empresa).first():
                flash('El RUT ya está registrado', 'error')
                return redirect(url_for('admin.registrar_empresa'))

            # Crear nueva empresa
            new_user = Empresa(
                nombre=nombre,
                telefono=telefono,
                email=email,
                rubro=rubro,
                descripcion=descripcion,
                rut_empresa=rut_empresa,
                password=generate_password_hash(password, method='pbkdf2:sha256'),
            )

            # Validar y establecer sitio web si existe
            if sitio_web:
                try:
                    new_user.set_sitio_web(sitio_web)
                except ValueError as e:
                    flash(f'Error en el sitio web: {str(e)}', 'error')
                    return redirect(url_for('admin.registrar_empresa'))

            # Guardar en la base de datos
            db.session.add(new_user)
            db.session.commit()
            
            flash('Empresa registrada exitosamente', 'success')
            return redirect(url_for('admin.empresas'))

        except Exception as e:
            db.session.rollback()
            flash('Error al registrar la empresa: ' + str(e), 'error')
            current_app.logger.error(f"Error registrando empresa: {str(e)}")
            return redirect(url_for('admin.registrar_empresa'))
            
    # GET request
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
@login_required
def ofertas():
    return render_template('manejo_de_empresas/ofertas.html')

@admin_bp.route('/admin/ubicaciones')
@login_required
def ubicaciones():
    return render_template('manejo_de_empresas/ubicaciones.html')

@admin_bp.route('/admin/ubicaciones/add', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
def delete_oferta(oferta_id):
    oferta = Oferta.query.get(oferta_id)
    if not oferta:
        flash('Oferta not found')
        return redirect(url_for('admin.ofertas'))

    db.session.delete(oferta)
    db.session.commit()

    flash('Oferta deleted successfully')
    return redirect(url_for('admin.ofertas'))

##########################################################################################
####### Importar empresas desde un archivo CSV ###########################################
from .forms.adminForms_empresa import ImportarEmpresasForm, ImportarOfertasForm
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def generar_contraseña(nombre, rut):
    """Genera una contraseña basada en el nombre y RUT de la empresa"""
    nombre_limpio = ''.join(e for e in nombre if e.isalnum())
    rut_limpio = ''.join(e for e in rut if e.isalnum())
    contraseña = f"{nombre_limpio[:4]}{rut_limpio[-4:]}"
    return contraseña

@admin_bp.route('/importar_empresas_csv', methods=['POST'])
@login_required
def importar_empresas_csv():
    # Verificar que el usuario actual es un administrador
    if not isinstance(current_user, Administrador):
        flash('No tienes permisos para realizar esta acción', 'error')
        return redirect(url_for('admin.empresas'))
        
    try:
        logger.debug("Iniciando proceso de importación de empresas")
        logger.debug(f"Usuario actual: {current_user.__class__.__name__}")
                
        if 'file' not in request.files:
            logger.warning("No se encontró archivo en la solicitud")
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(url_for('admin.empresas'))
        
        file = request.files['file']
        if file.filename == '':
            logger.warning("Nombre de archivo vacío")
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(url_for('admin.empresas'))

        if not file.filename.endswith('.csv'):
            logger.warning("Archivo no es CSV")
            flash('El archivo debe ser de tipo CSV', 'error')
            return redirect(url_for('admin.empresas'))
        
        # Guardar el ID del usuario administrador actual
        admin_id = current_user.id

        # Crear directorio si no existe
        if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
            os.makedirs(current_app.config['UPLOAD_FOLDER'])

        empresas_exitosas = []
        empresas_fallidas = []
        
        # Campos obligatorios
        campos_obligatorios = ['MARCAS', 'EMAIL', 'RUT']  # Actualizado para coincidir con el CSV

        try:
            # Leer CSV con encoding UTF-8
            df = pd.read_csv(file, encoding='utf-8')
            logger.debug(f"Columnas en el CSV: {df.columns.tolist()}")
            
            # Verificar campos obligatorios
            campos_faltantes = [campo for campo in campos_obligatorios if campo not in df.columns]
            if campos_faltantes:
                logger.error(f"Faltan campos obligatorios: {campos_faltantes}")
                flash(f'El archivo CSV no contiene los siguientes campos obligatorios: {", ".join(campos_faltantes)}', 'error')
                return redirect(url_for('admin.empresas'))

            # Procesar cada fila
            for index, row in df.iterrows():
                try:
                    # Verificar valores obligatorios
                    valores_faltantes = [campo for campo in campos_obligatorios if pd.isna(row[campo])]
                    
                    if valores_faltantes:
                        empresas_fallidas.append({
                            'empresa': row['MARCAS'] if 'MARCAS' in row and not pd.isna(row['MARCAS']) else f'Fila {index + 2}',
                            'fila': index + 2,
                            'razon': f'Faltan campos obligatorios: {", ".join(valores_faltantes)}',
                            'datos': row.to_dict()
                        })
                        continue

                    # Verificar si el email ya existe
                    if Empresa.query.filter_by(email=row['EMAIL']).first():
                        empresas_fallidas.append({
                            'empresa': row['MARCAS'],
                            'fila': index + 2,
                            'razon': 'Email ya registrado',
                            'datos': row.to_dict()
                        })
                        continue

                    # Generar contraseña
                    contraseña = generar_contraseña(str(row['MARCAS']), str(row['RUT']))

                    # Crear nueva empresa
                    nueva_empresa = Empresa(
                        nombre=row['MARCAS'],
                        email=row['EMAIL'],
                        rut_empresa=row['RUT'],
                        password=generate_password_hash(contraseña, method='pbkdf2:sha256'),
                        telefono=row.get('TELEFONO', ''),
                        rubro=row.get('RUBRO', ''),
                        descripcion=row.get('DESCRIPCIÓN', '')
                    )
                    
                    # Validar y establecer sitio web si existe
                    if 'SITIO WEB' in row and not pd.isna(row['SITIO WEB']):
                        try:
                            nueva_empresa.set_sitio_web(row['SITIO WEB'])
                        except ValueError as e:
                            logger.warning(f"URL inválida para {row['MARCAS']}: {str(e)}")


                    db.session.add(nueva_empresa)
                    empresas_exitosas.append({
                        'empresa': row['MARCAS'],
                        'email': row['EMAIL'],
                        'contraseña': contraseña
                    })

                except Exception as e:
                    logger.error(f"Error procesando fila {index + 2}: {str(e)}")
                    empresas_fallidas.append({
                        'empresa': row.get('MARCAS', f'Fila {index + 2}'),
                        'fila': index + 2,
                        'razon': str(e),
                        'datos': row.to_dict()
                    })

            db.session.commit()
            
            # Recargar el usuario administrador después de la importación
            admin_user = Administrador.query.get(admin_id)
            if admin_user:
                logout_user()
                login_user(admin_user)
                logger.debug(f"Usuario recargado: {current_user.__class__.__name__}")

            logger.info(f"Proceso completado: {len(empresas_exitosas)} exitosas, {len(empresas_fallidas)} fallidas")

            # Generar archivos CSV de resultados
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Archivo de empresas exitosas
            if empresas_exitosas:
                df_exitosas = pd.DataFrame(empresas_exitosas)
                exitosas_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f'empresas_creadas_{timestamp}.csv')
                df_exitosas.to_csv(exitosas_path, index=False, encoding='utf-8')
                logger.info(f"Archivo de empresas exitosas creado: {exitosas_path}")

            # Archivo de empresas fallidas
            if empresas_fallidas:
                df_fallidas = pd.DataFrame(empresas_fallidas)
                fallidas_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f'empresas_fallidas_{timestamp}.csv')
                df_fallidas.to_csv(fallidas_path, index=False, encoding='utf-8')
                logger.info(f"Archivo de empresas fallidas creado: {fallidas_path}")

            flash(f'Proceso completado: {len(empresas_exitosas)} empresas creadas, {len(empresas_fallidas)} fallidas', 'success')
            
            # Si hay empresas creadas exitosamente, descargar archivo con credenciales
            if empresas_exitosas:
                return send_file(
                    exitosas_path,
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name=f'credenciales_empresas_{timestamp}.csv'
                )

        except Exception as e:
            logger.error(f"Error general en el procesamiento: {str(e)}")
            db.session.rollback()
            flash(f'Error al procesar el archivo: {str(e)}', 'error')

    except Exception as e:
        logger.error(f"Error crítico: {str(e)}")
        flash('Error crítico en el proceso de importación', 'error')

    return redirect(url_for('admin.empresas'))


##########################################################################################
####### Importar ofertas desde un archivo CSV ###########################################
@admin_bp.route('/importar_ofertas_csv', methods=['POST'])
@login_required
def importar_ofertas_csv():
    if not isinstance(current_user, Administrador):
        flash('No tienes permisos para realizar esta acción', 'error')
        return redirect(url_for('admin.empresas'))
        
    try:
        logger.debug("Iniciando proceso de importación de ofertas")
        
        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(url_for('admin.empresas'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(url_for('admin.empresas'))

        if not file.filename.endswith('.csv'):
            flash('El archivo debe ser de tipo CSV', 'error')
            return redirect(url_for('admin.empresas'))

        # Crear directorio si no existe
        if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
            os.makedirs(current_app.config['UPLOAD_FOLDER'])

        ofertas_exitosas = []
        ofertas_fallidas = []
        
        try:
            df = pd.read_csv(file, encoding='utf-8')
            
            # Verificar campos obligatorios
            campos_obligatorios = ['empresa', 'titulo', 'descripcion', 'tipo', 'fecha_inicio', 'activa']
            campos_faltantes = [campo for campo in campos_obligatorios if campo not in df.columns]
            if campos_faltantes:
                flash(f'El archivo CSV no contiene los campos obligatorios: {", ".join(campos_faltantes)}', 'error')
                return redirect(url_for('admin.empresas'))

            # Procesar cada fila
            for index, row in df.iterrows():
                try:
                    nombre_empresa = str(row['empresa']).strip()
                    empresa = Empresa.query.filter(
                        db.func.lower(Empresa.nombre) == db.func.lower(nombre_empresa)
                    ).first()

                    # Buscar la empresa
                    if not empresa:
                        # Intentar búsqueda más flexible
                        empresa = Empresa.query.filter(
                            db.func.lower(Empresa.nombre).contains(db.func.lower(nombre_empresa)) |
                            db.func.lower(nombre_empresa).contains(db.func.lower(Empresa.nombre))
                        ).first()
                    
                    if not empresa:
                        raise ValueError(f"Empresa no encontrada: {nombre_empresa}")


                    # Crear nueva oferta
                    nueva_oferta = Oferta(
                        titulo=row['titulo'],
                        descripcion=row['descripcion'],
                        tipo=row['tipo'],
                        porcentaje_descuento=row.get('porcentaje_descuento'),
                        precio=row.get('precio'),
                        fecha_inicio=datetime.strptime(row['fecha_inicio'], '%Y-%m-%d'),
                        fecha_fin=datetime.strptime(row['fecha_fin'], '%Y-%m-%d') if pd.notna(row.get('fecha_fin')) else None,
                        activa=row['activa'],
                        empresa_id=empresa.id
                    )

                    db.session.add(nueva_oferta)
                    ofertas_exitosas.append({
                        'empresa': row['empresa'],
                        'titulo': row['titulo'],
                        'tipo': row['tipo']
                    })

                except Exception as e:
                    logger.error(f"Error procesando fila {index + 2}: {str(e)}")
                    ofertas_fallidas.append({
                        'fila': index + 2,
                        'razon': str(e),
                        'datos': row.to_dict()
                    })

            db.session.commit()
            flash(f'Proceso completado: {len(ofertas_exitosas)} ofertas creadas, {len(ofertas_fallidas)} fallidas', 'success')

        except Exception as e:
            logger.error(f"Error en el procesamiento: {str(e)}")
            db.session.rollback()
            flash(f'Error al procesar el archivo: {str(e)}', 'error')

    except Exception as e:
        logger.error(f"Error crítico: {str(e)}")
        flash('Error crítico en el proceso de importación', 'error')

    return redirect(url_for('admin.empresas'))
