from flask import Flask, request, jsonify
from flask import render_template
from flask.ext.bcrypt import Bcrypt
from models import User

app = Flask(__name__)
bcrypt = Bcrypt(app)



@app.route("/")
def index_route():
	return render_template('index.html')

@app.route("/signup", methods=['GET', 'POST'])
def sign_up():
	if request.method == 'POST':
		#Getting username and password
		#hashing password and creating a database entry and
		#returning true or returning to signup page
		attempted_username = request.form['username']
		attempted_password = request.form['password']
		pass_hash = brypt.generate_password_hash(attempted_password)
		User.create(username = attempted_username)
		User.create(password = pass_hash)
		return jsonify({"response": True})
	else:
		return render_template('signup.html')
