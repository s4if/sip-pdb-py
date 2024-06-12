import os

from flask import Flask, session, redirect, url_for
from . import auth, registrant
from werkzeug.security import check_password_hash, generate_password_hash
from .config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .db import db, init_app
from flask_wtf.csrf import CSRFProtect
from .helper import login_required, htmx

csrf = CSRFProtect()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    init_app(app)
    csrf.init_app(app)
    htmx.init_app(app)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    @app.route('/home')
    @login_required
    def home():
        return 'Home'    
    
    @app.route('/hash/<string:password>')
    def hash(password):
        return generate_password_hash(password)
    
    @app.route('/coba_layout')
    def coba_layout():
        from flask import render_template
        return render_template('layout.jinja')
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(registrant.bp)
    

    return app

# biar terdeteksi semua modulnya
from .models import *