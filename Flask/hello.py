from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
def hello_world():
	return 'Hello World!'

@app.route('/projects/')
def projects():
	return 'The project page'

@app.route('/about')
def about():
	return 'The about page'
@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
	return render_template('hello.html',name=name)

if __name__ == '__main__':
	app.run()