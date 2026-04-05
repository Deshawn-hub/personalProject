from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import IntegerField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange

class LoginForm(FlaskForm):
    username  = StringField('Username', validators=[DataRequired()])
    password  = PasswordField('Password', validators=[DataRequired()])
    submit    = SubmitField('Login')


class SignUpForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=80)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=80)])
    username = StringField('Username', validators=[DataRequired(), Length(max=80)])
    email = StringField('Email', validators=[DataRequired(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match.')],
    )
    submit = SubmitField('Create Account')

class PropertyForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    no_of_rooms = IntegerField('Number of Bedrooms', validators=[DataRequired(), NumberRange(min=1)])
    no_of_bathrooms = IntegerField('Number of Bathrooms', validators=[DataRequired(), NumberRange(min=1)])
    price = StringField('Price', validators=[DataRequired()])
    property_type = SelectField('Type', choices=[('house', 'House'), ('apartment', 'Apartment')], validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    photo = FileField('Photo', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])

    def __init__(self, *args, require_photo=True, **kwargs):
        super().__init__(*args, **kwargs)
        if require_photo:
            self.photo.validators = [
                FileRequired(),
                FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!'),
            ]
