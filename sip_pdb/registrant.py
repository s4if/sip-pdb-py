import datetime, os
from flask import (
    Blueprint, g, jsonify, render_template, request, session, url_for, send_from_directory, get_flashed_messages
)
from sqlalchemy.exc import IntegrityError
from .db import db
from .helper import htmx, login_required, admin_required
from .config import uploaddir

bp = Blueprint('registrant', __name__, url_prefix='/pendaftar')

# TODO: Implementasi blok belum-bayar per rute
# saat ini mainkan menu saja

@bp.route('/')
@login_required
def beranda():
    from .models import Registrant
    notif = {}
    fl_msg = get_flashed_messages(with_categories=True)
    for category, message in fl_msg:
        notif[category] = message
    rg = Registrant.query.filter_by(id=session['user_id']).first()
    return render_template('registrant/beranda.jinja', 
                           username=session['username'],
                           is_admin=session['is_admin'], 
                           is_htmx=htmx,
                           show_menu=session['show_menu'],
                           rg=rg,
                           p_code=str(rg.id).zfill(3),
                           **notif
                           )
    
@bp.route('/edit_profil', methods=('GET', 'POST'))
@login_required
def edit_profil():
    from .forms import RegisterForm
    from .models import Registrant
    rg = Registrant.query.filter_by(id=session['user_id']).first()
    if request.method == 'GET':
        form = RegisterForm()
        form.name.data = rg.name
        form.prev_school.data = rg.prev_school
        form.nisn.data = rg.nisn
        form.cp.data = rg.cp
        form.gender.data = rg.gender
        form.selection_path.data = rg.selection_path
        form.program.data = rg.program
        return render_template('registrant/edit_profil.jinja', 
                               username=session['username'], 
                               is_admin=session['is_admin'], 
                               form=form, 
                               is_htmx=htmx,
                               show_menu=session['show_menu'])
    if request.method == 'POST':
        form = RegisterForm(request.form)
        if (form.name.validate(form) and
                form.prev_school.validate(form) and
                form.nisn.validate(form) and
                form.cp.validate(form) and
                form.selection_path.validate(form) and
                form.program.validate(form)
            ):
            if request.form['selection_path'] != 'Jalur Reguler' and request.form['program'] == 'Industri':
                error="Mohon maaf, Pendaftar jalur seleksi Non-Reguler tidak bisa memilih Kelas Industri."
                return render_template('registrant/edit_profil.jinja', 
                                   username=session['username'], 
                                   is_admin=session['is_admin'], 
                                   form=form, 
                                   is_htmx=htmx,
                                   error=error,
                                   show_menu=session['show_menu'])
                
            rg.name = form.name.data
            rg.prev_school = form.prev_school.data
            rg.nisn = form.nisn.data
            rg.cp = form.cp.data
            rg.selection_path = form.selection_path.data
            rg.program = form.program.data
            db.session.add(rg)
            db.session.commit()
            success = "Profil anda telah diperbarui"
            return render_template('registrant/edit_profil.jinja', 
                                   username=session['username'], 
                                   is_admin=session['is_admin'], 
                                   form=form, 
                                   is_htmx=htmx,
                                   success=success,
                                   show_menu=session['show_menu'])
        else:
            error = "Mohon maaf, terjadi kesalahan. Silahkan coba lagi."
            return render_template('registrant/edit_profil.jinja', 
                                   username=session['username'], 
                                   is_admin=session['is_admin'], 
                                   form=form, 
                                   is_htmx=htmx,
                                   error=error,
                                   show_menu=session['show_menu'])
        
    

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
            is_admin=session['is_admin'], 
            form=form, 
            photo_uploaded=pu, 
            is_htmx=htmx,
            show_menu=session['show_menu'],)
    
    form = RegistrantDataForm(request.form)
    if not form.validate():
        error="Penyimpanan data gagal. Silahkan cek lagi data anda"
        return render_template('registrant/isi_data.jinja', 
                                show_menu=session['show_menu'],
                                is_admin=session['is_admin'], 
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
            is_admin=session['is_admin'], 
            step="Data Pendaftar",
            show_menu=session['show_menu'],
            next_url=url_for('registrant.isi_ortu', tipe='ayah'),
            prev_url=url_for('registrant.isi_data'),
            is_htmx=htmx
        )
    except IntegrityError:
        error="Penyimpanan data gagal, ada data yang salah. Silahkan coba lagi"
        return render_template('registrant/isi_data.jinja', show_menu=session['show_menu'], username=session['username'],
                           is_admin=session['is_admin'],  error=error, photo_uploaded=pu, is_htmx=htmx)
    
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
            is_admin=session['is_admin'], 
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
            is_admin=session['is_admin'], 
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
            rg.father_id = parent.id
            prev_url = url_for('registrant.isi_ortu', tipe='ayah')
            next_url = url_for('registrant.isi_ortu', tipe='ibu')
            step = "Data Ayah"
            
        elif tipe == 'ibu':
            rg.mother_id = parent.id
            prev_url = url_for('registrant.isi_ortu', tipe='ibu')
            next_url = url_for('registrant.isi_pernyataan')
            step = "Data Ibu"
            opt_url = url_for('registrant.isi_ortu', tipe='wali')
            opt_url_text = "Isi Data Wali (Bila Perlu)"
            
        elif tipe == 'wali':
            rg.guardian_id = parent.id
            prev_url = url_for('registrant.isi_ortu', tipe='wali')
            next_url = url_for('registrant.isi_pernyataan')
            step = "Data Wali"
            
        db.session.add(rg)
        db.session.commit()
        return render_template(
            'registrant/notif.jinja', 
            username=session['username'],
            is_admin=session['is_admin'], 
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
            is_admin=session['is_admin'], 
            show_menu=session['show_menu'],
            form=form, 
            error=error, 
            tipe=tipe, 
            is_htmx=htmx
            )
        
def offset_bpm(bpm):
    from .models import Registrant
    offset = {
        'Jalur Reguler': {
                'infaq_pendidikan': 1, #tidak ada potongan
                'spp': 1, #tidak ada potongan
                'wakaf_tanah': 1 #tidak ada potongan
            },
        'Jalur Beasiswa Dhuafa': {
                'infaq_pendidikan': 0.5, #potongan 50%
                'spp': 0.8, #potongan 20%
                'wakaf_tanah': 1 #tidak ada potongan
            },
        'Jalur Beasiswa Prestasi Nasional': {
                'infaq_pendidikan': 0, #potongan 100%
                'spp': 0.6, #potongan 40%
                'wakaf_tanah': 1 #tidak ada potongan
            },
        'Jalur Beasiswa Prestasi Provinsi': {
                'infaq_pendidikan': 0.8, #potongan 20%
                'spp': 0.8, #potongan 20%
                'wakaf_tanah': 1 #tidak ada potongan
            },
        'Jalur Beasiswa Tahfidz 10 Juz': {
                'infaq_pendidikan': 0.8, #potongan 20%
                'spp': 0.8, #potongan 20%
                'wakaf_tanah': 1 #tidak ada potongan
            },
        'Jalur Beasiswa Tahfidz 20 Juz': {
                'infaq_pendidikan': 0.6, #potongan 40%
                'spp': 0.7, #potongan 30%
                'wakaf_tanah': 1 #tidak ada potongan
            },
    }
    data = {}
    rg = Registrant.query.filter_by(id=session['user_id']).first()
    for k, v in bpm.items():
        data[k] = int(v * offset[rg.selection_path][k])
    return data
        
@bp.route('/isi_pernyataan', methods=('GET', 'POST'))
@login_required
def isi_pernyataan():
    error = None
    from .config import PDB_CONFIG
    from .models import Registrant
    biaya_tetap = PDB_CONFIG['biaya_tetap']
    tahun_masuk = PDB_CONFIG['tahun_masuk']
    rg = Registrant.query.filter_by(id=session['user_id']).first()
    bpm = offset_bpm(PDB_CONFIG['biaya_pendidikan_minimal']) # bpm -> biaya pendidikan minimal
    if rg.program == 'Industri' and rg.selection_path == 'Jalur Reguler': # kelas industri tambah 200K
        bpm['spp'] = bpm['spp'] + 200000
    
    fv = { # fv -> Form Value
        'icost' : 0,
        'scost' : 0,
        'lcost' : 0,
        'main_parent' : 'father',
        'qurban': ''
    }
    if request.method == 'POST':
        failure = []
        fv['icost'] = int(request.form['raw_icost'])
        if fv['icost'] not in range(bpm['infaq_pendidikan'], bpm['infaq_pendidikan']+2000001):
            fv['icost'] = int(request.form['other_icost'])
            if fv['icost'] < bpm['infaq_pendidikan'] + 2000000:
                failure.append('Isian Khusus Infaq Pendidikan tidak boleh kurang dari Rp. ' +
                               "{:,.0f}".format(bpm['infaq_pendidikan'] + 2000000).replace(",", ".") + ',-')
                
        fv['scost'] = int(request.form['raw_scost'])
        if fv['scost'] not in range(bpm['spp'], bpm['spp']+200001): # hotfix spp
            fv['scost'] = int(request.form['other_scost'])
            if fv['scost'] < bpm['spp'] + 200000: 
                failure.append('Isian Khusus SPP tidak boleh kurang dari Rp. ' +
                               "{:,.0f}".format(bpm['spp'] + 200000).replace(",", ".") + ',-')
                
        fv['lcost'] = int(request.form['raw_lcost'])
        if fv['lcost'] not in range(bpm['wakaf_tanah'], bpm['wakaf_tanah']+200001): # hotfix wakaf
            fv['lcost'] = int(request.form['other_lcost'])
            if fv['lcost'] < bpm['wakaf_tanah'] + 200000: 
                failure.append('Isian Khusus Wakaf Tanah tidak boleh kurang dari Rp. ' +
                               "{:,.0f}".format(bpm['wakaf_tanah'] + 200000).replace(",", ".") + ',-')
                
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
            rg.set_reg_id() # reg_id di set setelah ada surat pernyataan dan di re-set di finalisasi
            db.session.add(rg)
            db.session.commit()
            prev_url = url_for('registrant.isi_ortu', tipe='ibu')
            next_url = url_for('registrant.rekap')
            step = "Surat Pernyataan"
        
            return render_template(
                'registrant/notif.jinja', 
                username=session['username'],
                is_admin=session['is_admin'], 
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
        is_admin=session['is_admin'], 
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
    datadir = os.path.join(uploaddir, session['username'])
    pu = os.path.isfile(os.path.join(datadir, f'{session["user_id"]}_foto.png'))
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
    
    notif = {}
    fl_msg = get_flashed_messages(with_categories=True)
    for category, message in fl_msg:
        notif[category] = message
        
    return render_template('registrant/rekap.jinja', username=session['username'], 
                           is_admin=session['is_admin'], 
                           is_htmx=htmx, 
                           show_menu=session['show_menu'],
                           rg=rg,
                           pu=pu,
                           rgd=rgd, 
                           pd=parent_data,
                           **notif)

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
    # Validate the tipe parameter to prevent arbitrary file access
    if tipe not in ['foto', 'kwitansi']:  # add valid types here
        return 'Tipe tidak valid', 400

    datadir = os.path.join(uploaddir, str(session['username']))
    filepath = os.path.join(datadir, f'{session["user_id"]}_{tipe}.png')

    # Check if the file exists and is a file (not a directory)
    if os.path.isfile(filepath) and not os.path.isdir(filepath):
        # Use send_from_directory to prevent directory traversal attacks
        return send_from_directory(datadir, f'{session["user_id"]}_{tipe}.png', mimetype='image/png')
    else:
        return 'Foto tidak ditemukan', 404


@bp.route('/get_doc/<string:filename>')
@login_required
def get_doc(filename):
    datadir = os.path.join(uploaddir, str(session['username']))
    filepath = os.path.join(datadir, filename)
    if os.path.isfile(filepath):
        # Validate the file type to prevent arbitrary file access
        if not filename.endswith(('.png')):
            return 'Tipe file tidak valid', 400
        # Use send_from_directory to prevent directory traversal attacks
        return send_from_directory(datadir, filename, mimetype='image/png')
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
    tgl_bayar = request.form['tgl_bayar']
    rg.reg_fee = int(request.form['jumlah'])
    rg.reg_payment_date = datetime.datetime.strptime(tgl_bayar, '%Y-%m-%d').date()
    rg.verified_status = 0
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
                           is_admin=session['is_admin'], 
                           is_htmx=htmx,
                           show_menu=session['show_menu'],
                           rg=rg,
                           p_code=str(rg.id).zfill(3),
                           error='File harus bertipe .jpg, .jpeg, atau .png'
                           ) 

    img = Image.open(f) # kwitansi jangan resize
    img.save(os.path.join(datadir, f'{session["user_id"]}_kwitansi.png'))
    session['show_menu'] = not rg.finalized
    return render_template('registrant/beranda.jinja', 
                           username=session['username'], 
                           is_admin=session['is_admin'], 
                           is_htmx=htmx, 
                           show_menu=session['show_menu'],
                           rg=rg,
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
                           is_admin=session['is_admin'], 
                            is_htmx=htmx,
                            show_menu=session['show_menu'],
                            rg=rg,
                            p_code=str(rg.id).zfill(3),
                            error='Anda telah menyelesaikan pendaftaran.'
                            )
        else:
            return render_template(
                'registrant/finalisasi.jinja',
                show_menu=session['show_menu'],
                username=session['username'], 
                is_admin=session['is_admin'], 
                is_htmx=htmx, 
                )
        
        
    if request.method == 'POST':
        rg.finalized = True
        rg.set_reg_id()
        db.session.add(rg)
        db.session.commit()
        session['show_menu'] = False
        return render_template('registrant/beranda.jinja', 
                            username=session['username'], 
                            is_admin=session['is_admin'], 
                            is_htmx=htmx, 
                            show_menu=session['show_menu'],
                            rg=rg,
                            p_code=str(rg.id).zfill(3),
                            success='Anda telah menyelesaikan pendaftaran.'
                            )
        
@bp.route('/upload_dokumen', methods=['POST', 'GET'])
@login_required
def upload_dokumen():
    from .models import Document
    from .forms import DocumentForm
    from werkzeug.utils import secure_filename
    from sqlalchemy.exc import IntegrityError
    from PIL import Image
    form = DocumentForm()
    docs = Document.query.filter_by(registrant_id=session['user_id']).all()
    if request.method == 'GET':
        return render_template(
            'registrant/laman_upload.jinja', 
            show_menu=session['show_menu'], 
            username=session['username'],
            is_admin=session['is_admin'], 
            docs=docs,
            form=form,
            is_htmx=htmx
        )
    
    if request.method == 'POST':
        doc = Document()
        doc.registrant_id = session['user_id']
        doc.type = request.form['type']
        doc.issued_date = datetime.datetime.strptime(request.form['issued_date'], '%Y-%m-%d').date()
        doc.note = request.form['note']
        
        f = request.files['file']
        filename = secure_filename(f.filename)
        
        datadir = os.path.join(uploaddir, str(session['username']))
        if not os.path.isdir(datadir):
            os.mkdir(datadir)
    
        allowed_exts = {'.jpg', '.jpeg', '.png'}
        ext = os.path.splitext(filename)[1]
        if ext.lower() not in allowed_exts:
            error = 'File harus bertipe .jpg, .jpeg, atau .png'
            return render_template(
                'registrant/laman_upload.jinja', 
                show_menu=session['show_menu'], 
                is_admin=session['is_admin'], 
                username=session['username'],
                docs=docs,
                form=form,
                error=error,
                is_htmx=htmx
            )
        img = Image.open(f)
        hashstr = generate_hash()
        typestr = doc.type
        typestr = typestr.lower().replace(' ', '_')
        filename = f'{session["user_id"]}_{typestr}_{hashstr}.png'
        doc.filename = filename
        try :
            db.session.add(doc)
            db.session.commit()
            img.save(os.path.join(datadir, filename))
        except IntegrityError:
            db.session.rollback()
            error = 'Terjadi kesalahan dalam penyimpanan di database'
            return render_template(
                'registrant/laman_upload.jinja', 
                show_menu=session['show_menu'], 
                username=session['username'],
                is_admin=session['is_admin'], 
                docs=docs,
                form=form,
                error=error,
                is_htmx=htmx
            )
        docs.append(doc)
        success = 'Dokumen Berhasil di Upload.'
        return render_template(
            'registrant/laman_upload.jinja', 
            show_menu=session['show_menu'], 
            username=session['username'],
            is_admin=session['is_admin'], 
            docs=docs,
            form=form,
            success=success,
            is_htmx=htmx
        )

@bp.route('/delete_document/<string:filename>', methods=['GET'])
@login_required
def delete_document(filename):
    from .models import Document
    from .forms import DocumentForm
    doc = Document.query.filter_by(filename=filename).first()
    db.session.delete(doc)
    db.session.commit()
    datadir = os.path.join(uploaddir, str(session['username']))
    filepath = os.path.join(datadir, filename)
    if os.path.isfile(filepath):
        os.remove(filepath)
    
    form = DocumentForm()
    success = 'Dokumen Berhasil di Hapus.'
    docs = Document.query.filter_by(registrant_id=session['user_id']).all()
    return render_template(
            'registrant/laman_upload.jinja', 
            show_menu=session['show_menu'],
            is_admin=session['is_admin'],  
            username=session['username'],
            docs=docs,
            form=form,
            success=success,
            is_htmx=htmx
        )

def generate_hash():
    import hashlib
    import time
    timestamp = int(time.time() * 1000)  # get current timestamp in milliseconds
    hash_object = hashlib.md5(str(timestamp).encode())
    hash_hex = hash_object.hexdigest()[:8]  # use first 8 characters of the hash
    return hash_hex

@bp.route('/download/kartu_pendaftaran', methods=['GET'])
@login_required
def download_kartu_pendaftaran():
    from .models import Registrant, RegistrantData, Parent
    from .config import basedir, uploaddir
    from flask_weasyprint import HTML, render_pdf
    import base64
    rg = Registrant.query.filter_by(id=session['user_id']).first()
    rg.set_reg_id() # temporary
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
    
    bg_path = os.path.join(basedir, 'static', 'img', 'logo_smk.png')
    with open(bg_path, 'rb') as f:
        bg_data = f.read()
    bg_img = base64.b64encode(bg_data).decode('utf-8')
    
    datadir = os.path.join(uploaddir, str(session['username']))
    foto_path = os.path.join(datadir, f'{session["user_id"]}_foto.png')
    foto_img = ""
    if os.path.isfile(foto_path) and not os.path.isdir(foto_path):
        with open(foto_path, 'rb') as f:
            foto_data = f.read()
        foto_str = base64.b64encode(foto_data).decode('utf-8')
        foto_img = f"data:image/png;base64,{foto_str}"
        
    str_isi = render_template('registrant/kartu_pendaftaran.jinja',
                           bg_img=bg_img,
                           foto_img=foto_img,
                           rg=rg,
                           rgd=rgd, 
                           pd=parent_data)
    return render_pdf(HTML(string=str_isi))

@bp.route('/download/kartu_pendaftaran/admin/<int:reg_id>', methods=['GET'])
@admin_required
def download_kartu_pendaftaran_admin(reg_id):
    from .models import Registrant
    rg = Registrant.query.filter_by(id=reg_id).first()
    session['user_id'] = reg_id
    session['username'] = rg.username
    return_obj = download_kartu_pendaftaran()
    session.pop('user_id', None)
    session.pop('username', None)
    return return_obj

@bp.route('/download/surat_pernyataan', methods=['GET'])
@login_required
def download_surat_pernyataan():
    from flask_weasyprint import HTML, render_pdf
    from .models import Registrant, Parent
    from .config import PDB_CONFIG
    biaya_tetap = PDB_CONFIG['biaya_tetap']
    tahun_masuk = PDB_CONFIG['tahun_masuk']
    rg = Registrant.query.filter_by(id=session['user_id']).first()
    rg.set_reg_id() # temporary build reg_id
    dct_parent = {'father':'ayah', 'mother':'ibu', 'guardian':'wali'}
    type = dct_parent[rg.main_parent]
    parent = Parent.query.filter_by(id=str(session['user_id'])+'_'+type).first()
    total = 0
    for key in biaya_tetap.keys():
        total += biaya_tetap[key]
    
    total = total + rg.initial_cost + rg.monthly_cost + rg.land_donation
    now = datetime.datetime.now()
    bulan = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    tanggal = f'{now.day} {bulan[now.month]} {now.year}'
    
    
    str_isi = render_template('registrant/surat_pernyataan.jinja', 
                              rg=rg, parent=parent,
                              tahun_masuk=tahun_masuk,
                              total=total,
                              tanggal=tanggal,
                              **biaya_tetap)
    return render_pdf(HTML(string=str_isi))

@bp.route('/download/surat_pernyataan/admin/<int:reg_id>', methods=['GET'])
@admin_required
def download_surat_pernyataan_admin(reg_id):
    from .models import Registrant
    rg = Registrant.query.filter_by(id=reg_id).first()
    session['user_id'] = reg_id
    session['username'] = rg.username
    return_obj = download_surat_pernyataan()
    session.pop('user_id', None)
    session.pop('username', None)
    return return_obj

@bp.route('/data_pendaftar')
def data_pendaftar():
    from sqlalchemy.sql import text
    # define the query using the db.session object
    result = db.session.execute(text("""SELECT reg_id, name, prev_school, program 
                                     FROM registrants where deleted=FALSE;
                                     """))
    # fetch the results
    rows = result.fetchall()
    data = []
    for row in rows:
        data.append(tuple(row))
        
    return jsonify({'data':data})

@bp.route('/ganti_password', methods=['GET', 'POST'])
@login_required
def ganti_password():
    from werkzeug.security import generate_password_hash, check_password_hash
    if request.method == 'GET':
        return render_template(
            'registrant/ganti_password.jinja',
            show_menu=session['show_menu'],
            is_admin=session['is_admin'],  
            username=session['username'], 
            is_htmx=htmx)
    
    if request.method == 'POST':
        notif = {}
        from .models import Registrant
        rg = Registrant.query.filter_by(id=session['user_id']).first()
        if request.form['new_password'] != request.form['confirm_password']:
            notif['error'] = 'Konfirmasi password tidak sesuai'
        elif rg and check_password_hash(rg.password, request.form['current_password']):
            rg.password = generate_password_hash(request.form['new_password'])
            db.session.commit()
            notif['success'] = 'Password berhasil diubah'
        else:
            notif['error'] = 'Password lama tidak sesuai'
        return render_template(
            'registrant/ganti_password.jinja',
            show_menu=session['show_menu'],
            is_admin=session['is_admin'],  
            username=session['username'], 
            is_htmx=htmx, 
            **notif)
    
        