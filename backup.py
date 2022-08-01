from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

#Создаем инстанс фласка
app = Flask(__name__)
# создание базы sqlite
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

#новая база
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:4312@localhost/users'

# Секретный ключ
app.config['SECRET_KEY'] = "very extremely secret mega key"

#Инициализация базы
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Кое-что для фласк-авторизации
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

#Создание модели
class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), nullable=False, unique=True)
	name = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(100), nullable=False, unique=True)
	favorite_color = db.Column(db.String(100))
	date_added = db.Column(db.DateTime, default=datetime.utcnow)
	password_hash = db.Column(db.String(120), nullable=False)

	@property
	def password(self):
		raise AttributeError('Пароль нельзя прочитать')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	def __repr__(self):
		return '<Name %r>' % self.name

class Posts(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(70), nullable=False)
	content = db.Column(db.Text, nullable=False)
	author = db.Column(db.String(255), nullable=False)
	date_posted = db.Column(db.DateTime, default=datetime.utcnow)
	slug = db.Column(db.String(255), nullable=False)


class UserForm(FlaskForm):
	name = StringField("Имя", validators=[DataRequired()])
	username = StringField("Прозвище", validators=[DataRequired()])
	email = StringField("Почта", validators=[DataRequired()])
	favorite_color = StringField("Любимый цвет")
	password_hash = PasswordField("Придумайте пароль", validators=[DataRequired(), EqualTo('password_hash2', message='Пароли должны совпадать'),])
	password_hash2 = PasswordField("Подтвердите пароль", validators=[DataRequired()])
	submit = SubmitField("Подтвердить")
'''
Некоторые фильтры:
safe = нужен для вставки html кода на страницу. 
По умолчанию такой возможности нет в целях безопасности
capitalize = первая заглавная буква
lower = все прописные
upper = все заглавные
striptags = Полностью убирает html код из содержимого
title = каждое слово начинается с заглавной буквы
trip = удаляет конечные пробелы
'''

#Создаем форм-класс
class PostForm(FlaskForm):
	title = StringField("Название", validators=[DataRequired()])
	content = StringField("Содержание", validators=[DataRequired()], widget=TextArea())
	author = StringField("Автор", validators=[DataRequired()])
	slug = StringField("Слаг", validators=[DataRequired()])
	submit = SubmitField("Публиковать")

class NamesForm(FlaskForm):
	name = StringField("Вот из ё нейм", validators=[DataRequired()])
	submit = SubmitField("Подтвердить")

class PwForm(FlaskForm):
	email = StringField("Введите почту", validators=[DataRequired()])
	password_hash = PasswordField("Введите пароль", validators=[DataRequired()])
	submit = SubmitField("Подтвердить")
class LoginForm(FlaskForm):
	username = StringField("Введите логин", validators=[DataRequired()])
	password = PasswordField("Введите пароль", validators=[DataRequired()])
	submit = SubmitField("Подтвердить")

#Удаление	
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
	user_to_delete = Users.query.get_or_404(id)
	name = None
	form = UserForm()
	try:
		db.session.delete(user_to_delete)
		db.session.commit()
		flash("Пользователь удален")
		our_users = Users.query.order_by(Users.date_added)
		return render_template("add_user.html", 
			form=form,
			name=name,
			our_users=our_users)
	except:
		flash("Удаление не прошло успешно")
		return render_template("add_user.html", 
			form=form,
			name=name,
			our_users=our_users)



#Изменение данных
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
	form = UserForm()
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.favorite_color = request.form['favorite_color']
		name_to_update.username = request.form['username']
		try:
			db.session.add(name_to_update)
			db.session.commit()
			flash("Данные о пользователе изменены")
			return render_template("update.html",
				name_to_update=name_to_update, 
				form=form,
				id=id)
		except:
			flash("Ошибка. ОШИ-И-И-И-БКА")


	else:
		return render_template("update.html",
			form=form,
			name_to_update=name_to_update,
			id=id)


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
	name = None
	form = UserForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None:
			hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
			user = Users(name=form.name.data, username=form.username.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw)
			db.session.add(user)
			db.session.commit()
		name = form.name.data
		form.name.data = ''
		form.username.data = ''
		form.email.data = ''
		form.favorite_color.data = ''
		form.password_hash.data = ''
		form.password_hash2.data = ''
		flash("Пользователь успешно добавлен")
	our_users = Users.query.order_by(Users.date_added)
	return render_template("add_user.html", 
		form=form,
		name=name,
		our_users=our_users)


#Создаем декоратор
@app.route('/')

def index():
	first_name = "Игорь"
	stuff = "Хочешь этот дивный сок?"
	flavors = ["Яблочный", "Смородина", "Можевельник", "Томатный", "Мультифрукт"]
	return render_template("index.html", 
		first_name=first_name,
		stuff=stuff,
		flavors=flavors)

@app.route('/profile/<name>')
def profile(name):
	return render_template("profile.html", user_name=name)

@app.errorhandler(404)

def page_not_found(e):
	return render_template("404.html"), 404

@app.errorhandler(500)

def server_no_respond(e):
	return render_template("500.html"), 500

@app.route('/name', methods=['GET', 'POST'])
def name():
	name = None
	form = NamesForm()
	#Проверка
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
		flash("Заполнение формы было успешно")
	return render_template("name.html",
		name = name,
		form = form)
#тестирование системы авторизации
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
	email = None
	password = None
	pw_to_check = None
	passed = None
	form = PwForm()
	#Проверка
	if form.validate_on_submit():
		email = form.email.data
		password = form.password_hash.data
		form.email.data = ''
		form.password_hash.data = ''
		#Поиск пользователя по почте
		pw_to_check = Users.query.filter_by(email=email).first()

		#Проверка хешированного пароля
		passed = check_password_hash(pw_to_check.password_hash, password)
	return render_template("test_pw.html",
		email = email,
		password = password,
		pw_to_check=pw_to_check,
		passed=passed,
		form = form)

@app.route('/date')
def json_test_date():
	return {"Data": date.today()}

@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
	form = PostForm()

	if form.validate_on_submit():
		post = Posts(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
		form.title.data = ''
		form.content.data = ''
		form.author.data = ''
		form.slug.data = ''

		db.session.add(post)
		db.session.commit()

		flash("Вы опубликовали пост")

	return render_template("add_post.html", form=form)

@app.route('/posts')
def posts():
	posts = Posts.query.order_by(Posts.date_posted)
	return render_template("posts.html", posts=posts)

@app.route('/posts/<int:id>')
def post(id):
	post = Posts.query.get_or_404(id)
	return render_template("post.html", post=post)

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
	post = Posts.query.get_or_404(id)
	form = PostForm()
	if form.validate_on_submit():
		post.title=form.title.data
		post.content=form.content.data
		post.author=form.author.data
		post.slug=form.slug.data
		db.session.add(post)
		db.session.commit()
		flash('Пост отредактирован')
		return redirect(url_for('post', id=post.id))
	form.title.data = post.title
	form.author.data = post.author
	form.slug.data = post.slug
	form.content.data = post.content
	return render_template('edit_post.html', form=form, id=post.id)

@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
	post_to_delete = Posts.query.get_or_404(id)
	try:
		db.session.delete(post_to_delete)
		db.session.commit()
		flash("Пост удален")
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts=posts)
	except:
		flash("Ошибка. Пост не удален")
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(username=form.username.data).first()
		if user:
			if check_password_hash(user.password_hash, form.password.data):
				login_user(user)
				flash('Авторизация прошла успешно')
				return redirect(url_for('dashboard'))
			else:
				flash('Неправильный логин или пароль. Попробуйте еще раз')
		else:
			flash('Неправильный логин или пароль. Попробуйте еще раз')

	return render_template('login.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
	form = UserForm()
	id = current_user.id
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.favorite_color = request.form['favorite_color']
		name_to_update.username = request.form['username']
		try:
			db.session.add(name_to_update)
			db.session.commit()
			flash("Данные о пользователе изменены")
			return render_template("dashboard.html",
				name_to_update=name_to_update, 
				form=form,
				id=id)
		except:
			flash("Произошла ошибка")
			return render_template("dashboard.html", form=form,
				name_to_update=name_to_update)


	else:
		return render_template("dashboard.html",
			form=form,
			name_to_update=name_to_update,
			id=id)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
	logout_user()
	flash('Произведен выход из учетной записи')
	return redirect(url_for('login'))






