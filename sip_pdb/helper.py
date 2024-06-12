# isinya decorator untuk fungsi2 tertentu

import functools
from flask import session, redirect, url_for

from flask_htmx import HTMX

htmx = HTMX()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'is_admin' not in session:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


