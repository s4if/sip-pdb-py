from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError
from .db import db

bp = Blueprint('auth', __name__)

def create_captcha():
    from random import randint
    from captcha.image import ImageCaptcha
    import base64
    from io import BytesIO
    
    cap = ImageCaptcha()
    cap_int = str(randint(10000, 99999))
    session['captcha'] = cap_int
    cap_bytes = BytesIO()
    cap.write(str(cap_int), cap_bytes)
    cap_str = base64.b64encode(cap_bytes.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{cap_str}"

@bp.route('/register', methods=('GET', 'POST'))
def register():
    from .forms import RegisterForm
    if request.method == 'GET':
        cap_img = create_captcha()
        form = RegisterForm()
        return render_template('login/register.jinja', form=form, cap_img=cap_img)
    
    form = RegisterForm(request.form)
    if not form.validate():
        cap_img = create_captcha()
        error="Registrasi gagal. Silahkan cek lagi data anda"
        return render_template('login/register.jinja', form = form, error=error, cap_img=cap_img)
        
    if session['captcha'] != request.form['captcha']:
        cap_img = create_captcha()
        error="Registrasi gagal. Kolom Captcha tidak sesuai"
        return render_template('login/register.jinja', form = form, error=error, cap_img=cap_img)
    
    # TODO: buka dokumentasi kemudian sempurnakan dengan hash yang lebih aman
    hashed_password = generate_password_hash(request.form['password'], method='pbkdf2:sha256', salt_length=16) 
    from .models import Registrant
    r = Registrant()
    r.username = request.form['username']
    r.password = hashed_password
    r.name = request.form['name']
    r.gender = request.form['gender']
    r.prev_school = request.form['prev_school']
    r.nisn = request.form['nisn']
    r.cp = request.form['cp']
    r.program = request.form['program']
    r.selection_path = request.form['selection_path']
    r.entry_year = 2024 # sementara
    r.gelombang = 1
    r.registration_time = db.func.current_timestamp()

    # commit ke database
    try: 
        db.session.add(r)
        db.session.commit()
        success = "Registrasi berhasil. Silahkan login"
        return render_template('login/index.jinja',form = form, success=success)
    except IntegrityError:
        cap_img = create_captcha()
        error="Registrasi gagal, ada data yang salah. Silahkan coba lagi"
        form.username.errors.append('Username telah digunakan')
        return render_template('login/register.jinja', form = form, error=error, cap_img=cap_img)
        

@bp.route('/login', methods=['GET', 'POST'])
def login():
    from .forms import LoginForm
    form = LoginForm(request.form)
    if request.method == 'GET':
        # TODO: flash error dari login_required
        return render_template('login/index.jinja', form=form)
    else:
        from .models import Registrant
        r = Registrant.query.filter_by(username=request.form['username']).first()
        if r and check_password_hash(r.password, request.form['password']):
            # remember which user has logged in
            session['user_id'] = r.id
            session['username'] = r.username
            session['name'] = r.name
            session['logged_in'] = True
            session['is_admin'] = False
            session['show_menu'] = r.reg_fee > 0 and not r.finalized # TODO: cek lagi logic-nya
            return redirect(url_for('registrant.beranda'))
        else:
            error = 'Invalid username or password'
            return render_template('login/index.jinja', form=form, error=error)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))