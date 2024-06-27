import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from sqlalchemy.exc import IntegrityError
from .db import db
from .helper import htmx, login_required

bp = Blueprint('registrant', __name__, url_prefix='/pendaftar')

@bp.route('/')
@login_required
def beranda():
    return render_template('registrant/beranda.jinja', username=session['username'], is_htmx=htmx)

@bp.route('/isi_data', methods=('GET', 'POST'))
@login_required
def isi_data():
    from .forms import RegistrantDataForm
    from .models import RegistrantData
    rgd = RegistrantData.query.filter_by(id=session['user_id']).first()
    if request.method == 'GET':
        form = RegistrantDataForm(obj=rgd) if rgd else RegistrantDataForm()
        return render_template('registrant/isi_data.jinja', username=session['username'], form=form, is_htmx=htmx)
    
    form = RegistrantDataForm(request.form)
    if not form.validate():
        error="Penyimpanan data gagal. Silahkan cek lagi data anda"
        return render_template('registrant/isi_data.jinja', username=session['username'], form=form, error=error, is_htmx=htmx)
        
    if not rgd:
        rgd = RegistrantData()
    rgd.id = session['user_id']
    rgd.nik = request.form['nik']
    rgd.nkk = request.form['nkk']
    rgd.nak =  request.form['nak']
    rgd.birth_place = request.form['birth_place']
    rgd.birth_date = datetime.datetime.strptime(request.form['birth_date'], '%Y-%m-%d')
    rgd.birth_order = request.form['birth_order']
    rgd.siblings_count = request.form['siblings_count']
    rgd.street = request.form['street']
    rgd.rt = request.form['rt']
    rgd.rw = request.form['rw']
    rgd.village = request.form['village']
    rgd.district = request.form['district']
    rgd.city = request.form['city']
    rgd.province = request.form['province']
    rgd.country = request.form['country']
    rgd.postal_code = request.form['postal_code']
    rgd.parent_status = request.form['parent_status']
    rgd.nationality = request.form['nationality']
    rgd.religion = request.form['religion']
    rgd.height = request.form['height']
    rgd.weight = request.form['weight']
    rgd.head_size = request.form['head_size']
    rgd.stay_with = request.form['stay_with']
    # TODO: hobi, prestasi, catatan kesihatan, kelainan jasmani

    # commit ke database
    try: 
        db.session.add(rgd)
        db.session.commit()
        return render_template(
            'registrant/notif.jinja', 
            username=session['username'],
            step="Data Pendaftar",
            next_url=url_for('registrant.isi_wali'),
            prev_url=url_for('registrant.isi_data'),
            is_htmx=htmx
        )
    except IntegrityError:
        error="Penyimpanan data gagal, ada data yang salah. Silahkan coba lagi"
        return render_template('registrant/isi_data.jinja', username=session['username'], error=error, is_htmx=htmx)
    

@bp.route('/isi_wali')
@login_required
def isi_wali():
    return render_template('registrant/isi_wali.jinja', username=session['username'], is_htmx=htmx)

@bp.route('/isi_pernyataan')
@login_required
def isi_pernyataan():
    return render_template('registrant/isi_pernyataan.jinja', username=session['username'], is_htmx=htmx)

@bp.route('/rekap')
@login_required
def rekap():
    return render_template('registrant/rekap.jinja', username=session['username'], is_htmx=htmx)

