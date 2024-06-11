import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError
from .db import db

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=('GET', 'POST'))
def register():
    from .forms import RegisterForm
    if request.method == 'GET':
        form = RegisterForm()
        return render_template('login/register.jinja', form = form)
    
    form = RegisterForm(request.form)
    if not form.validate():
        error="Registrasi gagal. Silahkan cek lagi data anda"
        return render_template('login/register.jinja', form = form, error=error)
        
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
        return render_template('login/index.jinja',success=success)
    except IntegrityError:
        error="Registrasi gagal, ada data yang salah. Silahkan coba lagi"
        form.username.errors.append('Username telah digunakan')
        return render_template('login/register.jinja', form = form, error=error)
        

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login/index.jinja')
    else:
        from .models import Registrant
        r = Registrant.query.filter_by(username=request.form['username']).first()
        if r and check_password_hash(r.password, request.form['password']):
            # remember which user has logged in
            session['user_id'] = r.username
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            error = 'Invalid username or password'
            return render_template('login/index.jinja', error=error)


@bp.before_app_request
def load_logged_in_user():
   pass


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view