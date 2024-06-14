from flask_wtf import FlaskForm
from wtforms import  RadioField, SelectField, StringField, PasswordField, IntegerField, DateField
from wtforms.validators import DataRequired, EqualTo, InputRequired, Length, ValidationError
import phonenumbers

def validate_phone(form, field):
    if len(field.data) > 16:
        raise ValidationError('Invalid phone number.')
    try:
        input_number = phonenumbers.parse(field.data)
        if not (phonenumbers.is_valid_number(input_number)):
            raise ValidationError('Invalid phone number.')
    except phonenumbers.phonenumberutil.NumberParseException:
        # raise ValidationError('Phone number can\'t be parsed.')
        try: 
            int_data = int(field.data) # potential bug here?
            input_number = phonenumbers.parse("+62"+str(int_data))
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')
        except ValueError:
            raise ValidationError('Invalid phone number.')
        
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=15)])
    name = StringField('Nama Lengkap', validators=[DataRequired()])
    prev_school = StringField('Asal Sekolah', validators=[DataRequired()])
    nisn = StringField('NISN', validators=[DataRequired(),Length(min=10, max=10)])
    cp = StringField('Nomor Telepon', validators=[DataRequired(),validate_phone, Length(min=10, max=16)])
    gender = RadioField('Jenis Kelamin', choices=[('L', 'Laki-laki'), ('P', 'Perempuan')], validators=[DataRequired()])
    selection_path = SelectField('Jalur Seleksi Pendaftaran', choices=[
        ('Jalur Reguler', 'Jalur Reguler'),
        ('Jalur Beasiswa Dhuafa', 'Jalur Beasiswa Dhuafa'),
        ('Jalur Beasiswa Prestasi Nasional', 'Jalur Beasiswa Prestasi Nasional'),
        ('Jalur Beasiswa Prestasi Provinsi', 'Jalur Beasiswa Prestasi Provinsi'),
        ('Jalur Beasiswa Tahfidz 10 Juz', 'Jalur Beasiswa Tahfidz 10 Juz'),
        ('Jalur Beasiswa Tahfidz 20 Juz', 'Jalur Beasiswa Tahfidz 20 Juz')
    ], validators=[DataRequired()])
    program = SelectField('Program Pendidikan', choices=[('Reguler', 'Kelas Reguler'), ('Industri', 'Kelas Industri')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Konfirmasi Password', validators=[DataRequired(), EqualTo('password')])
    captcha = IntegerField('Captcha', validators=[InputRequired()])
    
class RegistrantDataForm(FlaskForm):
    nik = StringField('NIK', validators=[DataRequired(), Length(min=16, max=16)])
    nkk = StringField('Nomor KK', validators=[DataRequired(), Length(min=16, max=16)])
    nak = StringField('No. Akta Kelahiran', validators=[DataRequired(), Length(max=60)])
    birth_place = StringField('Tempat lahir', validators=[DataRequired(), Length(max=60)])
    birth_date = DateField('Tanggal Lahir', validators=[DataRequired()])
    birth_order = IntegerField('Anak keberapa', validators=[DataRequired()])
    siblings_count = IntegerField('Dari berapa bersaudara', validators=[DataRequired()])
    street = StringField('Dusun', validators=[DataRequired()])
    rt = IntegerField('RT')
    rw = IntegerField('RW')
    village = StringField('Kelurahan', validators=[DataRequired()])
    district = StringField('Kecamatan', validators=[DataRequired()])
    city = StringField('Kota', validators=[DataRequired()])
    province = StringField('Provinsi', validators=[DataRequired()])
    country = StringField('Negara', validators=[DataRequired()])
    postal_code = IntegerField('Kode Pos', validators=[DataRequired()])
    parent_status = SelectField('Status Ortu', validators=[DataRequired()], choices=[
        ('Lengkap', 'Lengkap'),
        ('Cerai', 'Cerai'),
        ('Yatim', 'Yatim'),
        ('Piatu', 'Piatu'),
        ('Yatim Piatu', 'Yatim Piatu')
    ])
    nationality = SelectField('Kewarganegaraan', validators=[DataRequired()], choices=[
        ('Warga Negara Indonesia', 'WNI'),
        ('Warga Negara Asing', 'WNA')
    ])
    religion = SelectField('Agama', validators=[DataRequired()], choices=[
        ('Islam', 'Islam'),
        ('Kristen', 'Kriten'),
        ('Katolik', 'Katolik'),
        ('Hindu', 'Hindu'),
        ('Budha', 'Budha'),
        ('Konghucu', 'Konghucu'),
        ('Penganut Kepercayaan', 'Penganut Kepercayaan')
    ])
    height = IntegerField('Tinggi', validators=[DataRequired()])
    weight = IntegerField('Berat', validators=[DataRequired()])
    head_size = IntegerField('Lingkar Kepala', validators=[DataRequired()])
    stay_with = SelectField('Tinggal Bersama', validators=[DataRequired()], choices=[
        ('Orang Tua', 'Orang Tua'),
        ('Kakek Nenek','Kakek Nenek'),
        ('Kerabat', 'Kerabat'),
        ('Lainnya', 'Lainnya')
    ])
    #hobbies = StringField('Hobi')
    #achievements = StringField('Prestasi')
    #hospital_sheets = StringField('Riwayat Kesehatan')
    #physical_abnormalities = StringField('Kelainan Jasmani')