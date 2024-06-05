import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'GET':
        return render_template('login/register.jinja')
    else:
        username = request.form['username']
        password = request.form['password']
        return username + " "+password

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login/index.jinja')
    else:
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and check_password_hash(generate_password_hash('qwerty'), password):
            # remember which user has logged in
            session['user_id'] = username
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