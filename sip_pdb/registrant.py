from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError
from .db import db
from .helper import htmx

bp = Blueprint('registrant', __name__, url_prefix='/pendaftar')

@bp.route('/beranda')
def beranda():
    return render_template('registrant/beranda.jinja', is_htmx=htmx)

@bp.route('/isi_data')
def isi_data():
    return render_template('registrant/isi_data.jinja', is_htmx=htmx)

@bp.route('/isi_wali')
def isi_wali():
    return render_template('registrant/isi_wali.jinja', is_htmx=htmx)

@bp.route('/isi_pernyataan')
def isi_pernyataan():
    return render_template('registrant/isi_pernyataan.jinja', is_htmx=htmx)

@bp.route('/rekap')
def rekap():
    return render_template('registrant/rekap.jinja', is_htmx=htmx)