import os, datetime

from flask import Flask, session, redirect, url_for
from . import auth, registrant
from werkzeug.security import check_password_hash, generate_password_hash
from .config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .db import db, init_app
from flask_wtf.csrf import CSRFProtect
from .helper import login_required, htmx
from flask.cli import with_appcontext
import click
from .models import Admin

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
    
    @app.template_filter('format_date')
    def format_date(date_obj: datetime.date):
        return date_obj.strftime('%d %B %Y')
    
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
    
    @app.route('/')
    def root_dir():
        return redirect(url_for('auth.login'))
    
    @click.command()
    @click.option('--username', prompt='Username', help='The username to login with.')
    @click.option('--password', prompt='Password', help='The password to login with.', hide_input=True)
    @with_appcontext
    def add_admin_user(username, password):
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        """Add a new admin user to the database"""
        admin_user = Admin(username=username, password=hashed_password)
        db.session.add(admin_user)
        db.session.commit()
        print(f"Admin user '{username}' added successfully!")
        
    @click.command()
    @click.option('--username', prompt='Username', help='The username to login with.')
    @click.option('--password', prompt='Password', help='The password to login with.', hide_input=True)
    @with_appcontext
    def change_admin_user(username, password):
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        """Add a new admin user to the database"""
        admin_user = Admin.query.filter_by(username=username).first()
        if admin_user is None:
            print(f"Admin user '{username}' tidak ditemukan!")
        else:
            admin_user.password = hashed_password
            db.session.add(admin_user)
            db.session.commit()
            print(f"Admin user '{username}' diubah!")
    
    @click.command()
    @click.option('--username', prompt='Username', help='The username to login delete.')
    @with_appcontext
    def delete_admin_user(username):
        admin_user = Admin.query.filter_by(username=username).first()
        if admin_user is None:
            print(f"Admin user '{username}' tidak ditemukan!")
        else:
            db.session.delete(admin_user)
            db.session.commit()
            print(f"Admin user '{username}' dihapus!")

    app.register_blueprint(auth.bp)
    app.register_blueprint(registrant.bp)
    app.cli.add_command(add_admin_user)
    app.cli.add_command(delete_admin_user)
    app.cli.add_command(change_admin_user)
    

    return app

# biar terdeteksi semua modulnya
from .models import *