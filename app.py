from flask import Flask, request, jsonify
from flask import render_template
from flask import g
from flask_bcrypt import Bcrypt
from models import User, init_db, db
from peewee import IntegrityError

app = Flask(__name__)
bcrypt = Bcrypt(app)

@app.route("/", methods=['GET', 'POST'])
def index_route():
	if request.method == 'POST':
		if valid_login(request.form['username'], request.form['password']):
			return jsonify({"response": True})
		else:
			response = {
				'response': False,
				'error':  "invalid username/password"
			}
			return jsonify(response)
	
	return render_template('index.html')

@app.route("/signup", methods=['GET', 'POST'])
def sign_up():
	if request.method == 'POST':
		#Getting username and password
		#hashing password and creating a database entry and
		#returning true or returning to signup page
		attempted_username = request.form['username']
		attempted_password = request.form['password']
		pass_hash = bcrypt.generate_password_hash(attempted_password)
		try:
			User.create(username = attempted_username, password=pass_hash)
		except IntegrityError:
			return jsonify({"response": False, "error": "username already taken"})
		return jsonify({"response": True})
	else:
		return render_template('signup.html')

@app.route("/dashboard")
def dashboard():
	return render_template("dashboard.html")
	
def valid_login(attempted_username, attempted_password):
	try:
		user = User.get(User.username == attempted_username)
	except UserDoesNotExist:
		return False
	return bcrypt.check_password_hash(user.password, attempted_password)
