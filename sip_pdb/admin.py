import datetime, os
from flask import (
    Blueprint, g, jsonify, render_template, request, session, url_for, redirect, flash, get_flashed_messages, send_from_directory
)
from sqlalchemy.exc import IntegrityError
from .db import db
from .helper import htmx, admin_required
from .config import uploaddir

bp = Blueprint('admin', __name__, url_prefix='/admin')

# TODO: implementasi halaman lihat pendaftar dan dokumen
# TODO: implementasi download excel
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
    notif = {}
    fl_msg = get_flashed_messages(with_categories=True)
    for category, message in fl_msg:
        notif[category] = message
        
    return render_template('admin/lihat_pendaftar.jinja', admin_name=session['admin_name'], is_htmx=htmx, **notif)

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
    ps_string = ['Bukti Pembayaran Tidak Valid', 'Belum di verifikasi', 'Bukti Pembayaran Berhasil Diverifikasi']
    status = {
        'pembayaran': ps_string[rg.verified_status+1],
        'upload_foto': 'Foto Sudah Terupload' if pu else 'Foto Belum Terupload',
        'data_diri': 'Data Diri Sudah Terisi' if rgd else 'Data Diri Belum Terisi',
        'data_ayah': 'Data Ayah Sudah Terisi' if fd else 'Data Ayah Belum Terisi',
        'data_ibu': 'Data Ibu Sudah Terisi' if md else 'Data Ibu Belum Terisi', 
        'data_wali': 'Data Wali Sudah Terisi' if wd else 'Data Wali Belum Terisi'
    }
    
    return render_template('admin/lihat_profil.jinja', 
                           admin_name=session['admin_name'],
                           rg=rg,
                           docs=docs,
                           reg_id=reg_id, 
                           is_htmx=htmx,
                           status=status,
                           **notif
                        )

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
        # sementara langsung seperti inifinalized_str
        btn1 = ""
        if row.finalized:
            btn1 = """
            <a class="btn btn-sm btn-warning" hx-boost="false" href="{}">Undo Finaliasi</a>
                        """.format(url_for('admin.revert_finalization', username=row.username))
        btn2 = ""
        if session['is_superadmin']:
            btn2 = """<a class="btn btn-sm btn-secondary" hx-boost="false" 
                        href="{}">Masuk Sebagai Pendaftar</a>
                        """.format(url_for('admin.log_as_registrant', user_id=row.id))
        btn3 = """<a class="btn btn-sm btn-success" hx-boost="true" hx-target="#hx_content" 
                        href="{}">Lihat Pendaftar</a>
                        """.format(url_for('admin.lihat_pendaftar_detail', reg_id=row.id))
        item.append(btn1 + btn2 + btn3 +"""<a class="btn btn-sm btn-danger" onclick="del_modal({})">Delete</a>
                    """.format(url_for('admin.log_as_registrant', user_id=row.id), row.id))
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