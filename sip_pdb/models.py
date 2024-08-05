from sip_pdb import db
from sqlalchemy.orm import relationship

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
class Registrant(db.Model):
    __tablename__ = 'registrants'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(15), nullable=False, unique=True)
    reg_id = db.Column(db.String(15), nullable=True, unique=True)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String(60), nullable=False)
    upload_dir = db.Column(db.String, nullable=True)
    gender = db.Column(db.String(10), nullable=False)
    prev_school = db.Column(db.String(120), nullable=False)
    nisn = db.Column(db.String(10), nullable=False)
    cp = db.Column(db.String(18), nullable=False)
    program = db.Column(db.String(15), nullable=False)
    selection_path = db.Column(db.String(40), nullable=False)
    entry_year = db.Column(db.Integer, nullable=False)
    verified = db.Column(db.Boolean, nullable=False, default=False)
    finalized = db.Column(db.Boolean, nullable=False, default=False)
    deleted = db.Column(db.Boolean, nullable=False, default=False)
    gelombang = db.Column(db.Integer, nullable=False)
    registration_time = db.Column(db.DateTime, nullable=False)
    initial_cost = db.Column(db.BigInteger, nullable=True)
    monthly_cost = db.Column(db.BigInteger, nullable=True)
    land_donation = db.Column(db.BigInteger, nullable=True)
    buy_laptop = db.Column(db.Boolean, nullable=False, default=True)
    qurban = db.Column(db.String(60), nullable=True)
    registrant_data_id = db.Column(db.Integer, db.ForeignKey('registrant_data.id'), nullable=True)
    father_id = db.Column(db.String(8), db.ForeignKey('parents.id'), nullable=True)
    mother_id = db.Column(db.String(8), db.ForeignKey('parents.id'), nullable=True)
    guardian_id = db.Column(db.String(8), db.ForeignKey('parents.id'), nullable=True)
    registrant_data = relationship('RegistrantData', foreign_keys=[registrant_data_id], cascade='all, delete', lazy='joined')
    father = relationship('Parent', foreign_keys=[father_id], cascade='all, delete', lazy='select')
    mother = relationship('Parent', foreign_keys=[mother_id], cascade='all, delete', lazy='select')
    guardian = relationship('Parent', foreign_keys=[guardian_id], cascade='all, delete', lazy='select')
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
class RegistrantData(db.Model):
    __tablename__ = 'registrant_data'
    id = db.Column(db.Integer, primary_key=True)
    nik = db.Column(db.String(16), nullable=False)  # nomor induk kependudukan
    nkk = db.Column(db.String(16), nullable=False)  # nomor kartu keluarga
    nak = db.Column(db.String(60), nullable=False)  # nomor akte kelahiran
    birth_place = db.Column(db.String(60), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    birth_order = db.Column(db.Integer, nullable=False)  # anak ke...
    siblings_count = db.Column(db.Integer, nullable=False)  # jumlah saudara + si pendaftar
    street = db.Column(db.String, nullable=False)  # dusun
    rt = db.Column(db.Integer, nullable=True)  # rt
    rw = db.Column(db.Integer, nullable=True)  # rw
    village = db.Column(db.String, nullable=False)  # desa
    district = db.Column(db.String, nullable=False)  # kecamatan
    city = db.Column(db.String, nullable=False)  # kota
    province = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    postal_code = db.Column(db.Integer, nullable=False)
    parent_status = db.Column(db.String(30), nullable=False)  # ortu lengkap, yatim, piatu, yatim piatu
    nationality = db.Column(db.String(3), nullable=False) # WNI, WNA
    religion = db.Column(db.String(20), nullable=False)
    height = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    head_size = db.Column(db.Integer, nullable=False)
    stay_with = db.Column(db.String, nullable=False)  # tinggal dengan siapa
    hobbies = db.Column(db.String(1024), nullable=True)
    achievements = db.Column(db.String(1024), nullable=True)
    hospital_sheets = db.Column(db.String(1024), nullable=True)
    physical_abnormalities = db.Column(db.String(1024), nullable=True)
    
    def __repr__(self):
        return '<User {}>'.format(self.name)
    
class Parent(db.Model):
    __tablename__ = 'parents'
    id = db.Column(db.String(8), primary_key=True)
    type = db.Column(db.String(4), nullable=False) # tipe, Ayah, Ibu, Wali
    name = db.Column(db.String(60), nullable=False)
    nik = db.Column(db.String(16), nullable=False)
    status = db.Column(db.String(25), nullable=False)  # Hidup, Cerai, Almarhum
    birth_place = db.Column(db.String(60), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    street = db.Column(db.String)  # Dusun
    rt = db.Column(db.Integer)  # RT
    rw = db.Column(db.Integer)  # RW
    village = db.Column(db.String, nullable=False)  # Desa
    district = db.Column(db.String, nullable=False)  # Kecamatan
    city = db.Column(db.String, nullable=False)  # Kota
    province = db.Column(db.String, nullable=False)
    country = db.Column(db.String)
    postal_code = db.Column(db.Integer, nullable=False)
    contact = db.Column(db.String(18), nullable=False)  # Nomor Telepon
    relation = db.Column(db.String, nullable=False)  # Kandung, Tiri, Angkat
    nationality = db.Column(db.String, nullable=False)
    religion = db.Column(db.String, nullable=False)  # pake radio
    education_level = db.Column(db.String, nullable=False)  # tingkat pendidikan, sd, smp.. s3
    job = db.Column(db.String, nullable=False)
    position = db.Column(db.String)
    company = db.Column(db.String)
    income = db.Column(db.BigInteger, nullable=False, default=0)
    burden_count = db.Column(db.Integer, nullable=False, default=0)
    
    def __repr__(self):
        return '<User {}>'.format(self.name)