import datetime, os
from flask import (
    Blueprint, g, render_template, request, send_file, session, url_for
)
from sqlalchemy.exc import IntegrityError
from .db import db
from .helper import htmx, login_required
from .config import uploaddir

bp = Blueprint('registrant', __name__, url_prefix='/pendaftar')

# TODO: Implementasi blok belum-bayar per rute
# saat ini mainkan menu saja


@bp.route('/')
@login_required
def beranda():
    from .models import Registrant
    rg = Registrant.query.filter_by(id=session['user_id']).first()
    return render_template('registrant/beranda.jinja', 
                           username=session['username'], 
                           is_htmx=htmx,
                           show_menu=session['show_menu'],
                           reg_fee=rg.reg_fee,
                           finalized=rg.finalized,
                           p_code=str(rg.id).zfill(3)
                           )

@bp.route('/isi_data', methods=('GET', 'POST'))
@login_required
def isi_data():
    from .forms import RegistrantDataForm
    from .models import RegistrantData, Registrant
    
    rgd = RegistrantData.query.filter_by(id=session['user_id']).first()
    rg = Registrant.query.filter_by(id=session['user_id']).first()
    datadir = os.path.join(uploaddir, session['username'])
    pu = os.path.isfile(os.path.join(datadir, f'{session["user_id"]}_foto.png'))
    if request.method == 'GET':
        form = RegistrantDataForm(obj=rgd) if rgd else RegistrantDataForm()
        return render_template(
            'registrant/isi_data.jinja', 
            username=session['username'], 
            form=form, 
            photo_uploaded=pu, 
            is_htmx=htmx,
            show_menu=session['show_menu'],)
    
    form = RegistrantDataForm(request.form)
    if not form.validate():
        error="Penyimpanan data gagal. Silahkan cek lagi data anda"
        return render_template('registrant/isi_data.jinja', 
                                show_menu=session['show_menu'],
                                username=session['username'], 
                                form=form, error=error, 
                                photo_uploaded=pu, 
                                is_htmx=htmx)
        
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
    rgd.hobbies = request.form['hobbies']
    rgd.hospital_sheets = request.form['hospital_sheets']
    rgd.physical_abnormalities = request.form['physical_abnormalities']

    # commit ke database
    try: 
        db.session.add(rgd)
        db.session.commit()
        rg.registrant_data_id = rgd.id
        db.session.add(rg)
        db.session.commit()
        return render_template(
            'registrant/notif.jinja', 
            username=session['username'],
            step="Data Pendaftar",
            show_menu=session['show_menu'],
            next_url=url_for('registrant.isi_ortu', tipe='ayah'),
            prev_url=url_for('registrant.isi_data'),
            is_htmx=htmx
        )
    except IntegrityError:
        error="Penyimpanan data gagal, ada data yang salah. Silahkan coba lagi"
        return render_template('registrant/isi_data.jinja', show_menu=session['show_menu'], username=session['username'], error=error, photo_uploaded=pu, is_htmx=htmx)
    
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
        return render_template('registrant/beranda.jinja', show_menu=session['show_menu'], error=error, is_htmx=htmx)
    
    from .models import Parent, Registrant
    from .forms import ParentForm
    parent = Parent.query.filter_by(id=f"{session['user_id']}"+"_"+tipe).first()
    form = ParentForm(obj = parent) if parent else ParentForm()
    if not parent:
        parent = Parent()
        parent.id = f"{session['user_id']}"+"_"+tipe
        
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
            
    if request.method == 'GET':
        return render_template(
            'registrant/isi_ortu.jinja', 
            username=session['username'], 
            form=form,
            show_menu=session['show_menu'],
            form_url=url_for('registrant.isi_ortu', tipe=tipe),
            tipe=tipe, 
            is_htmx=htmx,
        )
    
    
    form = ParentForm(request.form)
    form.type.data = tipe
    if not form.validate():
        print(form.errors)
        return render_template(
            'registrant/isi_ortu.jinja', 
            username=session['username'], 
            form=form,
            form_url=url_for('registrant.isi_ortu', tipe=tipe),
            tipe=tipe, 
            show_menu=session['show_menu'],
            is_htmx=htmx,
            error="Penyimpanan data gagal. Silahkan cek lagi data anda"
        )
    
    parent.type = tipe
    parent.name = request.form['name']
    parent.nik = request.form['nik']
    parent.status = request.form['status']
    parent.birth_place = request.form['birth_place']
    parent.birth_date = datetime.datetime.strptime(request.form['birth_date'], '%Y-%m-%d')
    parent.contact = request.form['contact']
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
    
    rg = Registrant.query.filter_by(id=session['user_id']).first()
        
    # commit ke database
    try: 
        next_url = prev_url = opt_url = opt_url_text = step = None
        db.session.add(parent)
        db.session.commit()
        if tipe == 'ayah':
            rg.ayah = parent
            prev_url = url_for('registrant.isi_ortu', tipe='ayah')
            next_url = url_for('registrant.isi_ortu', tipe='ibu')
            step = "Data Ayah"
            
        elif tipe == 'ibu':
            rg.ibu = parent
            prev_url = url_for('registrant.isi_ortu', tipe='ibu')
            next_url = url_for('registrant.isi_pernyataan')
            step = "Data Ibu"
            opt_url = url_for('registrant.isi_ortu', tipe='wali')
            opt_url_text = "Isi Data Wali (Bila Perlu)"
            
        elif tipe == 'wali':
            rg.wali = parent
            prev_url = url_for('registrant.isi_ortu', tipe='wali')
            next_url = url_for('registrant.isi_pernyataan')
            step = "Data Wali"
            
        db.session.add(rg)
        db.session.commit()
        return render_template(
            'registrant/notif.jinja', 
            username=session['username'],
            step=step,
            show_menu=session['show_menu'],
            next_url=next_url,
            prev_url=prev_url,
            opt_url=opt_url,
            opt_url_text=opt_url_text,
            is_htmx=htmx
        )
        
    except IntegrityError:
        error="error pada database. silahkan kontak administrator"
        return render_template(
            'registrant/isi_ortu.jinja', 
            username=session['username'], 
            show_menu=session['show_menu'],
            form=form, 
            error=error, 
            tipe=tipe, 
            is_htmx=htmx
            )
        
@bp.route('/isi_pernyataan', methods=('GET', 'POST'))
@login_required
def isi_pernyataan():
    error = None
    from .config import PDB_CONFIG
    from .models import Registrant
    biaya_tetap = PDB_CONFIG['biaya_tetap']
    tahun_masuk = PDB_CONFIG['tahun_masuk']
    bpm=PDB_CONFIG['biaya_pendidikan_minimal'] # bpm -> biaya pendidikan minimal
    fv = { # fv -> Form Value
        'icost' : 0,
        'scost' : 0,
        'lcost' : 0,
        'main_parent' : 'father',
        'qurban': ''
    }
    rg = Registrant.query.filter_by(id=session['user_id']).first()
    if request.method == 'POST':
        failure = []
        fv['icost'] = int(request.form['raw_icost'])
        if fv['icost'] not in range(bpm['infaq_pendidikan'], bpm['infaq_pendidikan']+2000001):
            fv['icost'] = int(request.form['other_icost'])
            if fv['icost'] < bpm['infaq_pendidikan'] + 2000000:
                failure.append('Isian Khusus Infaq Pendidikan tidak boleh kurang dari Rp. ' +
                               "{:,.0f}".format(bpm['infaq_pendidikan'] + 2000000).replace(",", ".") + ',-')
                
        fv['scost'] = int(request.form['raw_scost'])
        if fv['scost'] not in range(bpm['spp'], bpm['spp']+1000001):
            fv['scost'] = int(request.form['other_scost'])
            if fv['scost'] < bpm['spp'] + 1000000:
                failure.append('Isian Khusus SPP tidak boleh kurang dari Rp. ' +
                               "{:,.0f}".format(bpm['spp'] + 1000000).replace(",", ".") + ',-')
                
        fv['lcost'] = int(request.form['raw_lcost'])
        if fv['lcost'] not in range(bpm['wakaf_tanah'], bpm['wakaf_tanah']+1000001):
            fv['lcost'] = int(request.form['other_lcost'])
            if fv['lcost'] < bpm['wakaf_tanah'] + 1000000:
                failure.append('Isian Khusus Wakaf Tanah tidak boleh kurang dari Rp. ' +
                               "{:,.0f}".format(bpm['wakaf_tanah'] + 1000000).replace(",", ".") + ',-')
                
        fv['main_parent'] = request.form['main_parent']
        if failure != []:
            error = '<br>'.join(failure)
        else : 
            rg.initial_cost = fv['icost']
            rg.monthly_cost = fv['scost']
            rg.land_donation = fv['lcost']
            rg.main_parent = fv['main_parent']
            qurban=[]
            if 'q1' in request.form:
                qurban.append(str(tahun_masuk))
            if 'q2' in request.form:
                qurban.append(str(tahun_masuk+1))
            if 'q3' in request.form:
                qurban.append(str(tahun_masuk+2))
            rg.qurban = ';'.join(qurban) if qurban != [] else ''
            db.session.add(rg)
            db.session.commit()
            prev_url = url_for('registrant.isi_ortu', tipe='ibu')
            next_url = url_for('registrant.rekap')
            step = "Surat Pernyataan"
        
            return render_template(
                'registrant/notif.jinja', 
                username=session['username'],
                step=step,
                next_url=next_url,
                prev_url=prev_url,
                is_htmx=htmx,
                show_menu=session['show_menu']
            )
    
    fv['icost'] = rg.initial_cost if rg.initial_cost else 0
    fv['scost'] = rg.monthly_cost if rg.monthly_cost else 0
    fv['lcost'] = rg.land_donation if rg.land_donation else 0
    fv['main_parent'] = rg.main_parent if rg.main_parent else 'father'
    fv['qurban'] = rg.qurban if rg.qurban else ''

    return render_template(
        'registrant/isi_pernyataan.jinja', 
        username=session['username'], 
        is_htmx=htmx, 
        bpm=bpm,
        fv=fv,
        error=error,
        show_menu=session['show_menu'],
        tahun_masuk=tahun_masuk,
        **biaya_tetap
        )
    

@bp.route('/rekap')
@login_required
def rekap():
    from .models import Registrant, RegistrantData, Parent
    rg = Registrant.query.filter_by(id=session['user_id']).first()
    rgd = RegistrantData.query.filter_by(id=session['user_id']).first()
    parent_data = {}
    fd = Parent.query.filter_by(id=str(session['user_id'])+'_ayah').first()
    if fd: 
        if fd.birth_date : parent_data['Ayah'] = fd
    md = Parent.query.filter_by(id=str(session['user_id'])+'_ibu').first()
    if md: 
        if md.birth_date : parent_data['Ibu'] = md
    wd = Parent.query.filter_by(id=str(session['user_id'])+'_wali').first()
    if wd: 
        if wd.birth_date : parent_data['Wali'] = wd
    return render_template('registrant/rekap.jinja', username=session['username'], 
                           is_htmx=htmx, 
                           show_menu=session['show_menu'],
                           rg=rg,
                           rgd=rgd, 
                           pd=parent_data)

@bp.route('/laman_upload')
@login_required
def laman_upload():
    return render_template('registrant/laman_upload.jinja', show_menu=session['show_menu'], username=session['username'], is_htmx=htmx)

@bp.route('/proses_foto', methods=['POST'])
@login_required
def proses_foto():
    from werkzeug.utils import secure_filename
    from PIL import Image
    
    f = request.files['file']
    filename = secure_filename(f.filename)
    datadir = os.path.join(uploaddir, str(session['username']))
    if not os.path.isdir(datadir):
        os.mkdir(datadir)
    
    allowed_exts = {'.jpg', '.jpeg', '.png'}
    ext = os.path.splitext(filename)[1]
    if ext.lower() not in allowed_exts:
        return 'STATUS: Error. <br>File harus bertipe .jpg, .jpeg, atau .png' #, 415
        # kalau error, htmx tidak swap, semetara tidak ada pesan error

    img = Image.open(f)
    img = img.resize((600, 800), Image.LANCZOS)
    img.save(os.path.join(datadir, f'{session["user_id"]}_foto.png'))
    url_foto = url_for('registrant.get_foto', tipe='foto')
    return f'STATUS: Foto Berhasil di Update. <a class="btn btn-info btn-sm" target="_blank" href="{url_foto}">Lihat Foto</a>', 200

@bp.route('/get_foto/<string:tipe>')
@login_required
def get_foto(tipe):
    datadir = os.path.join(uploaddir, str(session['username']))
    if os.path.isfile(os.path.join(datadir, f'{session["user_id"]}_{tipe}.png')):
        return send_file(os.path.join(datadir, f'{session["user_id"]}_{tipe}.png'), mimetype='image/png')
    else:
        return 'Foto tidak ditemukan', 404
    
@bp.route('/upload_kwitansi', methods=['POST'])
@login_required
def upload_kwitansi():
    from werkzeug.utils import secure_filename
    from PIL import Image
    from .models import Registrant
    
    rg = Registrant.query.filter_by(id=session['user_id']).first()    
    f = request.files['file']
    jumlah = request.form['jumlah']
    tgl_bayar = request.form['tgl_bayar']
    rg.reg_fee = jumlah
    rg.reg_payment_date = datetime.datetime.strptime(tgl_bayar, '%Y-%m-%d').date()
    db.session.add(rg)
    db.session.commit()
    filename = secure_filename(f.filename)
    datadir = os.path.join(uploaddir, str(session['username']))
    if not os.path.isdir(datadir):
        os.mkdir(datadir)
    
    allowed_exts = {'.jpg', '.jpeg', '.png'}
    ext = os.path.splitext(filename)[1]
    if ext.lower() not in allowed_exts:
        return render_template('registrant/beranda.jinja', 
                           username=session['username'], 
                           is_htmx=htmx,
                           show_menu=session['show_menu'],
                           reg_fee=rg.reg_fee,
                           finalized=rg.finalized,
                           p_code=str(rg.id).zfill(3),
                           error='File harus bertipe .jpg, .jpeg, atau .png'
                           ) 

    img = Image.open(f)
    img = img.resize((600, 800), Image.LANCZOS)
    img.save(os.path.join(datadir, f'{session["user_id"]}_kwitansi.png'))
    session['show_menu'] = not rg.finalized
    return render_template('registrant/beranda.jinja', 
                           username=session['username'], 
                           is_htmx=htmx, 
                           show_menu=session['show_menu'],
                           reg_fee=rg.reg_fee,
                           finalized=rg.finalized,
                           p_code=str(rg.id).zfill(3),
                           success='Kwitansi Berhasil di Upload.'
                           )
    
@bp.route('/finalisasi', methods=['POST', 'GET'])
@login_required
def finalisasi():
    from .models import Registrant
    rg = Registrant.query.filter_by(id=session['user_id']).first()
    if request.method == 'GET':
        if rg.finalized:
            return render_template('registrant/beranda.jinja', 
                            username=session['username'], 
                            is_htmx=htmx,
                            show_menu=session['show_menu'],
                            reg_fee=rg.reg_fee,
                            finalized=rg.finalized,
                            p_code=str(rg.id).zfill(3),
                            error='Anda telah menyelesaikan pendaftaran.'
                            )
        else:
            return render_template(
                'registrant/finalisasi.jinja',
                show_menu=session['show_menu'],
                username=session['username'], 
                is_htmx=htmx, 
                )
        
        
    if request.method == 'POST':
        rg.finalized = True
        db.session.add(rg)
        db.session.commit()
        session['show_menu'] = False
        return render_template('registrant/beranda.jinja', 
                            username=session['username'], 
                            is_htmx=htmx, 
                            show_menu=session['show_menu'],
                            reg_fee=rg.reg_fee,
                            finalized=rg.finalized,
                            p_code=str(rg.id).zfill(3),
                            success='Anda telah menyelesaikan pendaftaran.'
                            )