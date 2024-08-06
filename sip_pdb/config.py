import os
basedir = os.path.abspath(os.path.dirname(__file__))
instancedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../instance/'))
# Config for the flask
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(instancedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
# config for the apps (always arrays)
PDB_CONFIG = {
    'nama_sekolah' : 'SMKIT Ihsanul Fikri Mungkid',
    'nama_gelombang': 'Gelombang 1',
    'indeks_gelombang': 1,
    'tahun_masuk': 2025,
    'biaya_registrasi': 200000,
    'biaya_tetap': {
        'seragam' 			: 1800000,
        'dana_kegiatan' 	: 1750000,
        'dana_kesehatan' 	: 100000,
        'dana_buku' 		: 650000,
        'dana_praktik' 		: 500000,
        'majalah_kalender' 	: 120000,
    },
    'biaya_pendidikan_minimal': {
        'infaq_pendidikan': 4000000,
        'spp': 1000000,
        'wakaf_tanah': 500000
    }
}