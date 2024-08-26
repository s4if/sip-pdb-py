import datetime, os
from flask import (
    Blueprint, g, jsonify, render_template, request, send_file, session, url_for, send_from_directory
)
from sqlalchemy.exc import IntegrityError
from .db import db
from .helper import htmx, admin_required
from .config import uploaddir

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/')
@admin_required
def beranda():
    return render_template('admin/beranda.jinja', admin_name=session['admin_name'], is_htmx=htmx)

# TODO: Implement login sebagai pendaftar dengan memainkan isi session
'''
route admin/change_role/<int:user_id>
    -> get objek -> set username, user_id, name -> set show_menu selalu true -> redirect ke beranda pendaftar
route admin/back_to_admin/
    -> hapus username, user_id, name, show_menu -> redirect ke beranda admin
'''

@bp.route('/lihat_pendaftar', methods=['GET'])
@admin_required
def lihat_pendaftar():
    return render_template('admin/lihat_pendaftar.jinja', is_htmx=htmx)

@bp.route('/data_pendaftar', methods=['GET'])
@admin_required
def data_pendaftar():
    from .models import Registrant, Parent
    from sqlalchemy.orm import aliased
    father = aliased(Parent)
    mother = aliased(Parent)
    result = db.session.query(Registrant).\
        outerjoin(father, Registrant.father_id == father.id).\
        outerjoin(mother, Registrant.mother_id == mother.id).\
        filter(Registrant.deleted == False).with_entities(
            Registrant.id.label('id'), #0
            Registrant.reg_id.label('reg_id'), #1
            Registrant.name.label('name'), #2
            Registrant.prev_school.label('prev_school'), #3
            Registrant.selection_path.label('selection_path'), #4
            Registrant.program.label('program'), #5
            father.income.label('father_income'), #6
            mother.income.label('mother_income'), #7
        ).all()
    data = []
    for row in result:
        item = []
        item.append(row.id)
        item.append(row.reg_id)
        item.append(row.name)
        item.append(row.prev_school)
        item.append(row.selection_path)
        item.append(row.program)
        item.append(row.father_income)
        item.append(row.mother_income)
        item.append("""<button class="btn btn-sm btn-primary" hx-get="#">Edit</button>
                    <button class="btn btn-sm btn-danger" hx-get="#">Delete</button>""")
        data.append(item)
        
    return jsonify({'data':data})

# TODO: Masuk dan keluar ke akun pendaftar!