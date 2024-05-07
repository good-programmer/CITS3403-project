from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired()])
    submit = SubmitField('Register')
    
class PuzzleSubmissionForm(FlaskForm):
    puzzlename = StringField('Puzzle Name', validators=[DataRequired()])
    puzzle = StringField('Puzzle String', validators=[DataRequired(), Length(max=10), Regexp('^[a-zA-Z]*$', message='Only alphabetical characters allowed')])
    submit = SubmitField('Submit')