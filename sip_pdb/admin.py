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

'''
example of multi join
from sqlalchemy import aliased
normal_order_alias = aliased(Order)
black_friday_order_alias = aliased(Order)
result = db.session.query(Customer).\
    outerjoin(normal_order_alias, Customer.normal_order_id == normal_order_alias.id).\
    outerjoin(black_friday_order_alias, Customer.black_friday_order_id == black_friday_order_alias.id).\
    all()
'''

'''
example of labeling in sqlalchemy
result = db.session.query(Customer).outerjoin(Order, Customer.id == Order.customer_id).with_entities(
    Customer.name.label('name'),
    Order.name.label('item_name')
).all()
'''