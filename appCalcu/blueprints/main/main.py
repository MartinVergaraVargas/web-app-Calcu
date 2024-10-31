import os
from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app
from flask_login import login_required, current_user
from appCalcu.models import Empresa, Oferta, Ubicacion
from sqlalchemy import func
from appCalcu import db


main_bp = Blueprint("main", __name__, template_folder="templates")

@main_bp.route("/mat")
def bienvenida():
    return render_template('bienvenida.html')

@main_bp.route("/")
def index():
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    tipo = request.args.get('tipo', None)

    per_page = 12  # Number of offers per page

    # Query for offers with pagination
    offers_query = db.session.query(
        Oferta,
        Empresa.nombre.label('empresa_nombre')
    ).join(
        Empresa, Oferta.empresa_id == Empresa.id
    ).filter(
        Oferta.activa == True,
        Empresa.activo == True
    ).order_by(
        Oferta.fecha_inicio.desc()
    )

    # Apply type filter if specified
    if tipo:
        offers_query = offers_query.filter(Oferta.tipo == tipo.upper())

    # Order by date
    offers_query = offers_query.order_by(Oferta.fecha_inicio.desc())

    # Apply pagination
    pagination = offers_query.paginate(page=page, per_page=per_page, error_out=False)
    ofertas_paginadas = pagination.items

    # Process offers for template
    ofertas_procesadas = []
    for oferta, empresa_nombre in ofertas_paginadas:
        precio_mostrar = ""
        
        if oferta.tipo == 'PRODUCTO' or oferta.tipo == 'SERVICIO':
            if oferta.precio is not None:
                precio_mostrar = f"${oferta.precio:,.0f} CLP"
        elif oferta.tipo == 'DESCUENTO':
            if oferta.porcentaje_descuento is not None:
                precio_mostrar = f"{oferta.porcentaje_descuento}% OFF"

        ofertas_procesadas.append({
            'id': oferta.id,
            'titulo': oferta.titulo,
            'descripcion': oferta.descripcion or "",
            'precio_mostrar': precio_mostrar,
            'tipo': oferta.tipo,
            'empresa': empresa_nombre
        })

    return render_template('home.html', 
                         ofertas=ofertas_procesadas, 
                         pagination=pagination,
                         tipo_actual=tipo)



@main_bp.route("/nosotros")
def nosotros():
    return render_template('about.html')

# @main_bp.route('/empresa_dashboard')
# @login_required
# def empresa_dashboard():
#     return render_template('empresa_dashboard.html')

@main_bp.route('/Bienvenido/<nombre>')
def Bienvenida_nombre(nombre):
    return f'!Bienvenid@, {nombre}'

@main_bp.route('/configuracion')
def configuracion():
    return render_template('dashboard-base.html')

@main_bp.route("/empresas")
def empresas():
    # Obtener parámetros de la URL
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    categoria = request.args.get('categoria', '')
    per_page = 10  # Número de empresas por página

    # Construir la consulta base
    query = db.session.query(
        Empresa,
        func.count(Oferta.id).label('total_ofertas'),
        func.count(Ubicacion.id).label('total_ubicaciones')
    ).outerjoin(
        Oferta, (Empresa.id == Oferta.empresa_id) & (Oferta.activa == True)
    ).outerjoin(
        Ubicacion, (Empresa.id == Ubicacion.empresa_id) & (Ubicacion.activa == True)
    ).filter(
        Empresa.activo == True
    )

    # Aplicar filtro de búsqueda si existe
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Empresa.nombre.ilike(search_term),
                Empresa.descripcion.ilike(search_term),
                Empresa.rubro.ilike(search_term)
            )
        )

    # Aplicar filtro de categoría si existe
    if categoria:
        query = query.filter(Empresa.rubro == categoria)

    # Agrupar y ordenar
    query = query.group_by(Empresa.id).order_by(Empresa.nombre)

    # Realizar la paginación
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    empresas = pagination.items

    # Preparar los datos para el template
    empresas_data = []
    for empresa, total_ofertas, total_ubicaciones in empresas:
        sitio_web = empresa.sitio_web
        if sitio_web:
            # Asegurarse de que la URL tenga el protocolo
            if not sitio_web.startswith(('http://', 'https://')):
                sitio_web = 'https://' + sitio_web
            # Eliminar espacios en blanco
            sitio_web = sitio_web.strip()

        # Verificar si existe el logo de la empresa
        logo_filename = f"{empresa.nombre}.png"
        logo_path = os.path.join('static', 'images', 'logos_de_empresas', logo_filename)
        full_logo_path = os.path.join(current_app.root_path, logo_path)
        
        # Si existe el archivo, usar la ruta del logo, si no, usar el placeholder
        if os.path.exists(full_logo_path):
            logo_url = url_for('static', filename=f'images/logos_de_empresas/{logo_filename}')
        else:
            logo_url = '/api/placeholder/192/192'

        empresas_data.append({
            'id': empresa.id,
            'nombre': empresa.nombre,
            'descripcion': empresa.descripcion or "Sin descripción disponible",
            'rubro': empresa.rubro or "Rubro no especificado",
            'sitio_web': sitio_web,
            'total_ofertas': total_ofertas,
            'total_ubicaciones': total_ubicaciones,
            'logo_url': logo_url
        })


    # Obtener categorías únicas para el filtro
    categorias = db.session.query(Empresa.rubro).distinct().filter(
        Empresa.rubro.isnot(None),
        Empresa.activo == True
    ).all()
    categorias = [cat[0] for cat in categorias if cat[0]]  # Eliminar valores None

    return render_template(
        'empresas.html',
        empresas=empresas_data,
        pagination=pagination,
        search=search,
        categoria_actual=categoria,
        categorias=categorias
    )
