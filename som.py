from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

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




#Создание модели
class Users(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(100), nullable=False, unique=True)
	favorite_color = db.Column(db.String(100))
	date_added = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return '<Name %r>' % self.name

class UserForm(FlaskForm):
	name = StringField("Имя", validators=[DataRequired()])
	email = StringField("Почта", validators=[DataRequired()])
	favorite_color = StringField("Favorite Color")
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

class NamesForm(FlaskForm):
	name = StringField("Вот из ё нейм", validators=[DataRequired()])
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
		try:
			db.session.commit()
			flash("Данные о пользователе изменены")
			return render_template("update.html",
				form=form,
				name_to_update=name_to_update)
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
			user = Users(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data)
			db.session.add(user)
			db.session.commit()
		name = form.name.data
		form.name.data = ''
		form.email.data = ''
		form.favorite_color.data = '' 
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
	flavors = ["Яблочный", "Смородина", "Можевельник", "Томатный", "Кровь", "Мультифрукт"]
	return render_template("index.html", 
		first_name=first_name,
		stuff=stuff,
		flavors=flavors)

@app.route('/okor/<name>')

def user(name):
	return render_template("okor.html", user_name=name)

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


