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
    name = db.Column(db.String, nullable=False)
    upload_dir = db.Column(db.String, nullable=True)
    gender = db.Column(db.String(10), nullable=False)
    prev_school = db.Column(db.String, nullable=False)
    nisn = db.Column(db.String, nullable=True)
    cp = db.Column(db.String, nullable=True)
    program = db.Column(db.String(15), nullable=False)
    selection_path = db.Column(db.String(15), nullable=False)
    entry_year = db.Column(db.Integer, nullable=False)
    verified = db.Column(db.Boolean, nullable=False, default=False)
    finalized = db.Column(db.Boolean, nullable=False, default=False)
    deleted = db.Column(db.Boolean, nullable=False, default=False)
    gelombang = db.Column(db.Integer, nullable=False)
    registration_time = db.Column(db.DateTime, nullable=False)
    initial_cost = db.Column(db.BigInteger, nullable=True)
    subscription_cost = db.Column(db.BigInteger, nullable=True)
    land_donation = db.Column(db.BigInteger, nullable=True)
    buy_laptop = db.Column(db.Boolean, nullable=False, default=True)
    qurban = db.Column(db.String(60), nullable=True)
    registrant_data_id = db.Column(db.Integer, db.ForeignKey('registrant_data.id'), nullable=True)
    father_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=True)
    mother_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=True)
    guardian_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=True)
    registrant_data = relationship('RegistrantData', foreign_keys=[registrant_data_id], cascade='all, delete', lazy='select')
    father = relationship('Parent', foreign_keys=[father_id], cascade='all, delete', lazy='select')
    mother = relationship('Parent', foreign_keys=[mother_id], cascade='all, delete', lazy='select')
    guardian = relationship('Parent', foreign_keys=[guardian_id], cascade='all, delete', lazy='select')
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
class RegistrantData(db.Model):
    __tablename__ = 'registrant_data'
    id = db.Column(db.Integer, primary_key=True)
    nik = db.Column(db.String(60), nullable=False)  # nomor induk kependudukan
    nkk = db.Column(db.String(60), nullable=False)  # nomor kartu keluarga
    nak = db.Column(db.String, nullable=False)  # nomor akte kelahiran
    birth_place = db.Column(db.String, nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    birth_order = db.Column(db.String)  # anak ke...
    siblings_count = db.Column(db.String)  # sekarang, jumlah saudara + si pendaftar
    street = db.Column(db.String)  # dusun
    rt = db.Column(db.Integer)  # rt
    rw = db.Column(db.Integer)  # rw
    village = db.Column(db.String, nullable=False)  # desa
    district = db.Column(db.String, nullable=False)  # kecamatan
    city = db.Column(db.String, nullable=False)  # kota
    province = db.Column(db.String, nullable=False)
    country = db.Column(db.String)
    postal_code = db.Column(db.String, nullable=False)
    parent_status = db.Column(db.String, nullable=False)  # ortu lengkap, yatim, piatu, yatim piatu
    nationality = db.Column(db.String, nullable=False)
    religion = db.Column(db.String(10), nullable=False)
    hospital_sheets = db.Column(db.String(1024))
    physical_abnormalities = db.Column(db.String(1024))
    height = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    head_size = db.Column(db.Integer, nullable=False)
    stay_with = db.Column(db.String, nullable=False)  # tinggal dengan siapa
    hobbies = db.Column(db.String(1024))
    achievements = db.Column(db.String(1024))
    
    def __repr__(self):
        return '<User {}>'.format(self.name)
    
class Parent(db.Model):
    __tablename__ = 'parents'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String, nullable=False) # tipe, Ayah, Ibu, Wali
    name = db.Column(db.String, nullable=False)
    nik = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)  # Hidup, Cerai, Almarhum
    birth_place = db.Column(db.String, nullable=False)
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
    contact = db.Column(db.String)  # Nomor Telepon
    relation = db.Column(db.String, nullable=False)  # Kandung, Tiri, Angkat
    nationality = db.Column(db.String, nullable=False)
    religion = db.Column(db.String, nullable=False)  # pake radio
    education_level = db.Column(db.String, nullable=False)  # tingkat pendidikan, sd, smp.. s3
    job = db.Column(db.String)
    position = db.Column(db.String)
    company = db.Column(db.String)
    income = db.Column(db.BigInteger)
    burden_count = db.Column(db.Integer)
    
    def __repr__(self):
        return '<User {}>'.format(self.name)