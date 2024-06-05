import os

from flask import Flask, session, redirect, url_for
from . import auth
from .config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def init_app(app):
    db.init_app(app)
    migrate.init_app(app, db)

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    init_app(app)

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
    def home():
        if 'logged_in' not in session:
            return redirect(url_for('auth.login'))

        return 'Home'    
    
    app.register_blueprint(auth.bp)

    return app

# biar terdeteksi semua modulnya
from .models import *