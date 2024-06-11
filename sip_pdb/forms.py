from flask_wtf import FlaskForm
from wtforms import  RadioField, SelectField, StringField, PasswordField, IntegerField
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
        ('Jalur Beasiswa Hafidz 10 Juz', 'Jalur Beasiswa Tahfidz 10 Juz'),
        ('Jalur Beasiswa Hafidz 20 Juz', 'Jalur Beasiswa Tahfidz 20 Juz')
    ], validators=[DataRequired()])
    program = SelectField('Program Pendidikan', choices=[('Reguler', 'Kelas Reguler'), ('Industri', 'Kelas Industri')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Konfirmasi Password', validators=[DataRequired(), EqualTo('password')])
    captcha = IntegerField('Captcha', validators=[InputRequired()])