import datetime, os
from flask import (
    Blueprint, g, jsonify, send_file, render_template, request, session, url_for, redirect, flash, get_flashed_messages, send_from_directory
)
from sqlalchemy.exc import IntegrityError
from .db import db
from .helper import htmx, admin_required
from .config import uploaddir

bp = Blueprint('admin', __name__, url_prefix='/admin')

# TODO: implementasi download dokumen pendaftar

@bp.route('/')
@admin_required
def beranda():
    notif = {}
    fl_msg = get_flashed_messages(with_categories=True)
    for category, message in fl_msg:
        notif[category] = message
    
    return render_template(
        'admin/beranda.jinja', 
        admin_name=session['admin_name'], 
        is_htmx=htmx,
        **notif
)
    
@bp.route('/ganti_password', methods=['GET', 'POST'])
@admin_required
def ganti_password():
    from werkzeug.security import generate_password_hash, check_password_hash
    if request.method == 'GET':
        return render_template('admin/ganti_password.jinja', admin_name=session['admin_name'], is_htmx=htmx)
    
    if request.method == 'POST':
        notif = {}
        from .models import Admin
        admin = Admin.query.filter_by(username=session['admin_name']).first()
        if request.form['new_password'] != request.form['confirm_password']:
            notif['error'] = 'Konfirmasi password tidak sesuai'
        elif admin and check_password_hash(admin.password, request.form['current_password']):
            admin.password = generate_password_hash(request.form['new_password'])
            db.session.commit()
            notif['success'] = 'Password berhasil diubah'
        else:
            notif['error'] = 'Password lama tidak sesuai'
        return render_template('admin/ganti_password.jinja', admin_name=session['admin_name'], is_htmx=htmx, **notif)

@bp.route('/lihat_pendaftar', methods=['GET'])
@admin_required
def lihat_pendaftar():
    from .forms import RegisterForm
    notif = {}
    dl_form = RegisterForm()
    dl_form.selection_path.choices.append(('Semua', 'Semua'))
    dl_form.program.choices.append(('Semua', 'Semua'))
    fl_msg = get_flashed_messages(with_categories=True)
    for category, message in fl_msg:
        notif[category] = message
        
    return render_template('admin/lihat_pendaftar.jinja', dl_form=dl_form, admin_name=session['admin_name'], is_htmx=htmx, **notif)

@bp.route('/lihat_pendaftar/<int:reg_id>', methods=['GET'])
@admin_required
def lihat_pendaftar_detail(reg_id):
    notif = {}
    fl_msg = get_flashed_messages(with_categories=True)
    for category, message in fl_msg:
        notif[category] = message
    
    from .models import Registrant, RegistrantData, Document, Parent
    rg = Registrant.query.filter_by(id=reg_id).first()
    rgd = RegistrantData.query.filter_by(id=reg_id).first()
    datadir = os.path.join(uploaddir, rg.username)
    pu = os.path.isfile(os.path.join(datadir, f'{reg_id}_foto.png'))
    fd = Parent.query.filter_by(id=str(reg_id)+'_ayah').first()
    md = Parent.query.filter_by(id=str(reg_id)+'_ibu').first()
    wd = Parent.query.filter_by(id=str(reg_id)+'_wali').first()
    docs = Document.query.filter_by(registrant_id=reg_id).all()
    status = {
        'upload_foto': pu,
        'data_diri': rgd,
        'data_ayah': fd,
        'data_ibu': md, 
        'data_wali': wd,
        'surat_pernyataan': rg.initial_cost != 0 and rg.monthly_cost != 0 and rg.land_donation != 0,
    }
    
    return render_template('admin/lihat_profil.jinja', 
                           admin_name=session['admin_name'],
                           rg=rg,
                           docs=docs,
                           reg_id=reg_id, 
                           is_htmx=htmx,
                           status=status,
                           is_superadmin=session['is_superadmin'],
                           **notif
                        )
    
@bp.route('/download_dokumen_pendaftar/<int:reg_id>', methods=['GET'])
@admin_required
def download_dokumen_pendaftar(reg_id):
    from .models import Registrant
    import zipfile
    
    rg = Registrant.query.filter_by(id=reg_id).first()
    if not rg: 
        flash('Registrant tidak ditemukan', 'error')
        return redirect(url_for('admin.lihat_pendaftar'))
    
    datadir = os.path.join(uploaddir, rg.username)
    if not os.path.isdir(datadir):
        flash('Folder dokumen pendaftar tidak ditemukan', 'error')
        return redirect(url_for('admin.lihat_pendaftar'))
    try:
        zip_path = os.path.join(datadir, f'{rg.id}_{rg.username}.zip')
        with zipfile.ZipFile(zip_path, 'w') as zf:
            for root, dirs, files in os.walk(datadir):
                for f in files:
                    if f.endswith('.png') or f.endswith('.pdf'):
                        zf.write(os.path.join(root, f), os.path.relpath(os.path.join(root, f), datadir))
        return send_file(zip_path, as_attachment=True)
    except Exception as e:
        flash("Terjadi kesalahan saat membuat zip file", 'error')
        return redirect(url_for('admin.lihat_pendaftar'))
    finally:
        if os.path.isfile(zip_path):
            os.remove(zip_path)

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
            Registrant.finalized.label('finalized'), #8
            Registrant.username.label('username'), #9
            Registrant.cp.label('no_telp'), #10
            father.contact.label('no_telp_ayah'), #11
            mother.contact.label('no_telp_ibu') #12
        ).order_by(Registrant.id).all()
    data = []
    n = 1
    for row in result:
        item = []
        item.append(n)
        n+=1
        item.append(row.reg_id)
        item.append(row.username)
        item.append(row.name)
        item.append(row.prev_school)
        item.append(row.selection_path)
        item.append(row.program)
        item.append(row.no_telp)
        item.append(row.no_telp_ayah)
        item.append(row.no_telp_ibu)
        # sementara langsung seperti inifinalized_str
        item.append("""<div class="btn-group" role="group" >
                    <a class="btn btn-sm btn-primary" hx-boost="true" hx-target="#hx_content" 
                        href="{}">Lihat</a>
                    <a class="btn btn-sm btn-danger" onclick="del_modal({})">Hapus</a></div>
                    """.format(url_for('admin.lihat_pendaftar_detail', reg_id=row.id),row.id))
        data.append(item)
        
    return jsonify({'data':data})

@bp.route('/data_belum_bayar', methods=['GET'])
@admin_required
def data_belum_bayar():
    from .models import Registrant
    from sqlalchemy.orm import aliased
    rows = Registrant.query.filter(Registrant.deleted == False).\
        filter(Registrant.reg_fee <= 0).order_by(Registrant.id.desc()).all()
    data = []
    count = 1
    for row in rows:
        item = []
        item.append(count)
        count+=1
        item.append(row.name)
        item.append(row.prev_school)
        item.append(row.cp)
        item.append('''<a class="btn btn-sm btn-primary" hx-boost="true" hx-target="#hx_content" 
                        href="{}">Lihat</a>'''.format(url_for('admin.lihat_pendaftar_detail', reg_id=row.id)))
        data.append(item)
        
    return jsonify({'data':data})

@bp.route('/data_belum_lengkap', methods=['GET'])
@admin_required
def data_belum_lengkap():
    from .models import Registrant, RegistrantData, Parent
    from sqlalchemy.orm import aliased
    rgd = aliased(RegistrantData)
    father = aliased(Parent)
    mother = aliased(Parent)
    rows = db.session.query(Registrant).\
        outerjoin(rgd, Registrant.registrant_data_id == rgd.id).\
        outerjoin(father, Registrant.father_id == father.id).\
        outerjoin(mother, Registrant.mother_id == mother.id).\
        filter(Registrant.deleted == False).with_entities(
            Registrant.id.label('id'),
            Registrant.name.label('name'),
            Registrant.username.label('username'),
            Registrant.prev_school.label('prev_school'),
            Registrant.cp.label('cp'),
            Registrant.finalized.label('finalized'),
            rgd.nik.label('nik'),
            father.name.label('father_name'),
            mother.name.label('mother_name'),
        ).order_by(Registrant.id.desc()).all()
    data = []
    count = 1
    for row in rows:
        item = []
        item.append(count)
        count+=1
        item.append(row.name)
        item.append(row.prev_school)
        item.append(row.cp)
        datadir = os.path.join(uploaddir, row.username)
        pu = os.path.isfile(os.path.join(datadir, f'{row.id}_foto.png'))
        item.append('Sudah' if pu else 'Belum') # Upload Foto
        item.append("Belum" if not row.nik else "Sudah") # Data Diri
        item.append("Belum" if not row.father_name else "Sudah") # Data Ayah
        item.append("Belum" if not row.mother_name else "Sudah") # Data Ibu
        item.append("Sudah" if row.finalized else "Belum") # finalisasi
        item.append('''<a class="btn btn-sm btn-primary" hx-boost="true" hx-target="#hx_content" 
                        href="{}">Lihat</a>'''.format(url_for('admin.lihat_pendaftar_detail', reg_id=row.id)))
        if not all((pu, row.nik, row.father_name, row.mother_name, row.finalized)):
            data.append(item)
        
    return jsonify({'data':data})
    
@bp.route('/get_foto/<int:reg_id>/<string:tipe>')
@admin_required
def get_foto(reg_id, tipe):
    from .models import Registrant
    rg = Registrant.query.filter_by(id=reg_id).first()
    if not rg:
        return 'Pendaftar tidak ditemukan', 404
    
    # Validate the tipe parameter to prevent arbitrary file access
    if tipe not in ['foto', 'kwitansi']:  # add valid types here
        return 'Tipe tidak valid', 400

    datadir = os.path.join(uploaddir, str(rg.username))
    filepath = os.path.join(datadir, f'{reg_id}_{tipe}.png')

    # Check if the file exists and is a file (not a directory)
    if os.path.isfile(filepath) and not os.path.isdir(filepath):
        # Use send_from_directory to prevent directory traversal attacks
        return send_from_directory(datadir, f'{reg_id}_{tipe}.png', mimetype='image/png')
    else:
        return 'Foto tidak ditemukan', 404


@bp.route('/get_doc/<int:reg_id>/<string:filename>')
@admin_required
def get_doc(reg_id, filename):
    from .models import Registrant
    rg = Registrant.query.filter_by(id=reg_id).first()
    if not rg:
        return 'Pendaftar tidak ditemukan', 404
    
    datadir = os.path.join(uploaddir, str(rg.username))
    filepath = os.path.join(datadir, filename)
    if os.path.isfile(filepath):
        # Validate the file type to prevent arbitrary file access
        if not filename.endswith(('.png')):
            return 'Tipe file tidak valid', 400
        # Use send_from_directory to prevent directory traversal attacks
        return send_from_directory(datadir, filename, mimetype='image/png')
    else:
        return 'Foto tidak ditemukan', 404

@bp.route('/hapus_pendaftar', methods=['POST'])
@admin_required
def hapus_pendaftar():
    from .models import Registrant
    reg_id = request.form.get('reg_id')
    rg = Registrant.query.filter_by(id=reg_id).first()
    if rg is None:
        flash('Registrant tidak ditemukan', 'error')
        return redirect(url_for('admin.lihat_pendaftar'))
    
    rg.deleted = True
    db.session.add(rg)
    db.session.commit()
    flash('Registrant {} di hapus'.format(rg.name), 'success')
    return redirect(url_for('admin.lihat_pendaftar'))

@bp.route('/reset_password_pendaftar/<int:reg_id>', methods=['POST'])
@admin_required
def reset_password_pendaftar(reg_id):
    from .models import Registrant
    from werkzeug.security import generate_password_hash
    rg = Registrant.query.filter_by(id=reg_id).first()
    if rg is None:
        flash('Registrant tidak ditemukan', 'error')
        return redirect(url_for('admin.lihat_pendaftar_detail', reg_id=reg_id))
    
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    if new_password != confirm_password:
        flash('Konfirmasi password tidak sesuai', 'error')
        return redirect(url_for('admin.lihat_pendaftar_detail', reg_id=reg_id))
    
    rg.password = generate_password_hash(new_password)
    db.session.add(rg)
    db.session.commit()
    flash('Password pendaftar {} berhasil di reset'.format(rg.name), 'success')
    return redirect(url_for('admin.lihat_pendaftar_detail', reg_id=reg_id))

@bp.route('/restore_pendaftar/<int:reg_id>', methods=['GET'])
@admin_required
def restore_pendaftar(reg_id):
    # TODO: kasih konfirmasi, biar tidak auto restore
    from .models import Registrant
    rg = Registrant.query.filter_by(id=reg_id).first()
    if rg is None:
        flash('Registrant tidak ditemukan', 'error')
        return redirect(url_for('admin.lihat_pendaftar'))
    
    rg.deleted = False
    db.session.add(rg)
    db.session.commit()
    flash('Registrant {} berhasil dikembalikan'.format(rg.name), 'success')
    return redirect(url_for('admin.lihat_pendaftar'))

@bp.route('/lihat_pembayaran', methods=['GET'])
@admin_required
def lihat_pembayaran():
    notif = {}
    fl_msg = get_flashed_messages(with_categories=True)
    for category, message in fl_msg:
        notif[category] = message
        
    return render_template('admin/lihat_pembayaran.jinja', admin_name=session['admin_name'], is_htmx=htmx, **notif)

@bp.route('/data_pembayaran', methods=['GET'])
@admin_required
def data_pembayaran():
    from .models import Registrant
    rgs = Registrant.query.filter_by(deleted=False).all()
    data = []
    for row in rgs:
        item = []
        item.append(str(row.id).zfill(3))
        item.append(row.name)
        item.append(row.reg_fee)
        item.append("Belum Bayar" if row.reg_payment_date is None else row.reg_payment_date.strftime('%a, %d %B %Y'))
        status_str = ['Bukti Pembayaran Tidak Valid', 'Belum di verifikasi', 'Bukti Pembayaran Berhasil Diverifikasi']
        item.append(status_str[row.verified_status+1]) #disesuaikan dengan tema -1, 0, 1
        item.append("""<a class="btn btn-sm btn-primary" hx-boost="false" 
                    href="{}">Verifikasi</a>
                    """.format(url_for('admin.verifikasi_pembayaran', user_id=row.id)) if row.reg_fee > 0 else "")
        data.append(item)
    
    return jsonify({'data':data})

@bp.route('/log_as_registrant/<int:user_id>', methods=['GET'])
@admin_required
def log_as_registrant(user_id):
    from .models import Registrant
    rg = Registrant.query.filter_by(id=user_id).first()
    if rg is None:
        flash('Registrant tidak ditemukan', 'error')
        return redirect(url_for('admin.beranda'))
    
    if not session['is_superadmin']:
        flash('Role anda tidak bisa masuk sebagai registrant', 'error')
        return redirect(url_for('admin.beranda'))
    
    session['user_id'] = user_id
    session['username'] = rg.username
    session['show_menu'] = True
    flash('Login sebagai {} berhasil'.format(rg.name), 'success')
    return redirect(url_for('registrant.rekap'))

@bp.route('/back_to_admin', methods=['GET'])
@admin_required
def back_to_admin():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('show_menu', None)
    flash('Kembali ke akun Admin', 'info')
    return redirect(url_for('admin.beranda'))

@bp.route('/revert_finalization/<string:username>', methods=['GET'])
@admin_required
def revert_finalization(username):
    from .models import Registrant
    rg = Registrant.query.filter_by(username=username).first()
    if rg is None:
        flash('Registrant tidak ditemukan', 'error')
        return redirect(url_for('admin.beranda'))
    
    rg.finalized = False
    db.session.add(rg)
    db.session.commit()
    flash('Finalisasi pendaftar dengan nama {} telah dibatalkan'.format(rg.name), 'success')
    if session['is_superadmin']:
        session['show_menu'] = True
        return redirect(url_for('registrant.beranda'))
    else:
        return redirect(url_for('admin.beranda'))
        
@bp.route('/verifikasi_pembayaran/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def verifikasi_pembayaran(user_id):
    from .models import Registrant
    import base64
    rg = Registrant.query.filter_by(id=user_id).first()
    if rg is None:
        flash('Pendaftar dengan ID {} tidak ditemukan'.format(user_id), 'error')
        return redirect(url_for('admin.beranda'))
    
    if request.method == 'GET':
        datadir = os.path.join(uploaddir, str(rg.username))
        filepath = os.path.join(datadir, f'{rg.id}_kwitansi.png')

        # Check if the file exists and is a file (not a directory)
        str_img = ''
        if os.path.isfile(filepath) and not os.path.isdir(filepath):
            with open(filepath, 'rb') as f:
                raw_img = base64.b64encode(f.read()).decode('utf-8')
                str_img = f"data:image/png;base64,{raw_img}"
            
        return render_template(
            'admin/verifikasi_pembayaran.jinja', 
            admin_name=session['admin_name'], 
            is_htmx=htmx,
            str_img=str_img,
            rg=rg,
            user_id=user_id
        )
    
    if request.method == 'POST':
        rg.verified_status = request.form['hasil_verifikasi']
        db.session.add(rg)
        db.session.commit()
        flash('Pembayaran Pendaftar dengan nama {} telah diverifikasi'.format(rg.name), 'success')
        return redirect(url_for('admin.lihat_pembayaran'))