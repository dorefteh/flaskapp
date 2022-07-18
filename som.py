from flask import Flask, render_template

#Создаем инстанс фласка
app = Flask(__name__)

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