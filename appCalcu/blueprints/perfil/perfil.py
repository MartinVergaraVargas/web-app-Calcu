# appCalcu/blueprints/perfil/perfil.py
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from appCalcu import db
from .forms.admin_forms import AdminProfileForm
from .forms.empresa_forms import EmpresaProfileForm
from .forms.usuario_forms import UsuarioProfileForm

perfil_bp = Blueprint('perfil', __name__, template_folder='templates')

@perfil_bp.route('/perfil')
@login_required
def ver_perfil():
    return render_template('ver_perfil.html')

@perfil_bp.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    # Seleccionar el formulario correcto según el tipo de usuario
    if current_user.__class__.__name__ == 'CommonUser':
        form = UsuarioProfileForm()
    elif current_user.__class__.__name__ == 'Empresa':
        form = EmpresaProfileForm()
    else:
        form = AdminProfileForm()
    
    if request.method == 'GET':
        # Poblar el formulario con los datos actuales del usuario
        for field in form:
            if hasattr(current_user, field.name):
                field.data = getattr(current_user, field.name)
    
    if form.validate_on_submit():
        try:
            # Actualizar los datos del usuario
            for field in form:
                if hasattr(current_user, field.name):
                    setattr(current_user, field.name, field.data)
            
            db.session.commit()
            flash('Perfil actualizado correctamente', 'success')
            return redirect(url_for('perfil.ver_perfil'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar el perfil', 'error')
    
    return render_template('editar_perfil.html', form=form)