from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField

class SearchForm(FlaskForm):
	searched = StringField("Результаты", validators=[DataRequired()])
	submit = SubmitField("Подтвердить")

class UserForm(FlaskForm):
	name = StringField("Имя", validators=[DataRequired()])
	username = StringField("Прозвище", validators=[DataRequired()])
	email = StringField("Почта", validators=[DataRequired()])
	favorite_color = StringField("Любимый цвет")
	password_hash = PasswordField("Придумайте пароль", validators=[DataRequired(), EqualTo('password_hash2', message='Пароли должны совпадать'),])
	password_hash2 = PasswordField("Подтвердите пароль", validators=[DataRequired()])
	submit = SubmitField("Подтвердить")


#Создаем форм-класс
class PostForm(FlaskForm):
	title = StringField("Название", validators=[DataRequired()])
	content = CKEditorField('Содержание', validators=[DataRequired()])
	slug = StringField("Слаг", validators=[DataRequired()])
	submit = SubmitField("Публиковать")

class PwForm(FlaskForm):
	email = StringField("Введите почту", validators=[DataRequired()])
	password_hash = PasswordField("Введите пароль", validators=[DataRequired()])
	submit = SubmitField("Подтвердить")
class LoginForm(FlaskForm):
	username = StringField("Введите логин", validators=[DataRequired()])
	password = PasswordField("Введите пароль", validators=[DataRequired()])
	submit = SubmitField("Подтвердить")

