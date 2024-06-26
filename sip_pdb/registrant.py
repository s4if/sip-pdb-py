import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from sqlalchemy.exc import IntegrityError
from .db import db
from .helper import htmx, login_required

bp = Blueprint('registrant', __name__, url_prefix='/pendaftar')

def render_ortu(tipe, parent):
    from .forms import ParentForm
    form = ParentForm()
    form.type.data = tipe
    form.name.data = parent.name
    form.nik.data = parent.nik
    form.status.data = parent.status
    form.birth_place.data = parent.birth_place
    form.birth_date.data = parent.birth_date
    form.contact.data = parent.contact
    form.relation.data = parent.relation
    form.nationality.data = parent.nationality
    form.religion.data = parent.religion
    form.education_level.data = parent.education_level
    form.job.data = parent.job
    form.position.data = parent.position
    form.company.data = parent.company
    form.income.data = parent.income
    form.burden_count.data = parent.burden_count
    form.street.data = parent.street
    form.rt.data = parent.rt
    form.rw.data = parent.rw
    form.village.data = parent.village
    form.district.data = parent.district
    form.city.data = parent.city
    form.province.data = parent.province
    form.country.data = parent.country
    form.postal_code.data = parent.postal_code
    return render_template(
        'registrant/isi_ortu.jinja', 
        username=session['username'], 
        form=form,
        form_url=url_for('registrant.isi_ortu', tipe=tipe),
        tipe=tipe, 
        is_htmx=htmx
    )

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
            next_url=url_for('registrant.isi_wali'), #nanti diganti
            prev_url=url_for('registrant.isi_data'),
            is_htmx=htmx
        )
    except IntegrityError:
        error="Penyimpanan data gagal, ada data yang salah. Silahkan coba lagi"
        return render_template('registrant/isi_data.jinja', username=session['username'], error=error, is_htmx=htmx)
    
@bp.route('/clone_alamat', methods=['GET'])
@login_required
def clone_alamat():
    from .models import RegistrantData
    from .forms import ParentForm
    rgd = RegistrantData.query.filter_by(id=session['user_id']).first()
    form = ParentForm()
    form.street.data = rgd.street
    form.village.data = rgd.village
    form.rt.data = rgd.rt
    form.rw.data = rgd.rw
    form.district.data = rgd.district
    form.city.data = rgd.city
    form.province.data = rgd.province
    form.country.data = rgd.country
    form.postal_code.data = rgd.postal_code
    return render_template('registrant/clone_alamat.jinja', form=form)
    

@bp.route('/isi_ortu/<string:tipe>', methods=('GET', 'POST'))
@login_required
def isi_ortu(tipe):
    if tipe not in ['ayah', 'ibu','wali']:
        error="Mohon maaf, url tidak ditemukan."
        return render_template('registrant/beranda.jinja', error=error, is_htmx=htmx)
    
    from .models import Parent
    parent = Parent.query.filter_by(id=f"{session['user_id']}"+"_"+tipe).first()
    if not parent:
        parent = Parent()
        parent.id = f"{session['user_id']}"+"_"+tipe
        
    if request.method == 'GET':
        return render_ortu(tipe, parent)
    
    from .forms import ParentForm
    form = ParentForm(request.form)
    if not form.validate():
        return render_ortu(tipe, parent, form)
    
    parent.type = tipe
    parent.name = request.form['name']
    parent.nik = request.form['nik']
    parent.status = request.form['status']
    parent.birth_place = request.form['birth_place']
    parent.birth_date = datetime.datetime.strptime(request.form['birth_date'], '%Y-%m-%d')
    parent.relation = request.form['relation']
    parent.nationality = request.form['nationality']
    parent.religion = request.form['religion']
    parent.education_level = request.form['education_level']
    parent.job = request.form['job']
    parent.position = request.form['position']
    parent.company = request.form['company']
    parent.income = request.form['income']
    parent.burden_count = request.form['burden_count']
    parent.street = request.form['street']
    parent.rt = request.form['rt']
    parent.rw = request.form['rw']
    parent.village = request.form['village']
    parent.district = request.form['district']
    parent.city = request.form['city']
    parent.province = request.form['province']
    parent.country = request.form['country']
    parent.postal_code = request.form['postal_code']
    
    # commit ke database
    try: 
        db.session.add(parent)
        db.session.commit()
        return render_ortu(tipe, parent, form)
    except IntegrityError:
        error="Penyimpanan data gagal, ada data yang salah. Silahkan coba lagi"
        return render_ortu(tipe, parent, form, error)
    
    
    

#hanya biar gak error, nanti dihapus
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

