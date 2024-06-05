import os
basedir = os.path.abspath(os.path.dirname(__file__))
instancedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../instance/'))
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(instancedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False