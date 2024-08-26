# isinya decorator untuk fungsi2 tertentu

import functools
from flask import session, redirect, url_for

from flask_htmx import HTMX

htmx = HTMX()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'logged_in' not in session or 'is_admin' not in session:
            return redirect(url_for('auth.login'))
        elif session['logged_in'] == False:
            session.clear()
            return redirect(url_for('auth.login'))
        elif 'user_id' not in session \
            or 'username' not in session:
            # TODO: tambah pesan flash error
            # TODO: htmx disable hx-boost lewat server
            return redirect(url_for('admin.beranda'))
        return view(**kwargs)
    return wrapped_view

def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'is_admin' not in session or 'logged_in' not in session or 'admin_name' not in session:
            return redirect(url_for('auth.login_admin'))
        elif session['is_admin'] == False:
            session.clear()
            return redirect(url_for('auth.login_admin'))
        return view(**kwargs)
    return wrapped_view


