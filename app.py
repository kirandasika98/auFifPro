from flask import Flask, request, jsonify
from flask import render_template
from flask import g
from flask_bcrypt import Bcrypt
from models import User, init_db, db
from peewee import IntegrityError

app = Flask(__name__)
bcrypt = Bcrypt(app)

# @app.before_request
# def before_request():
# 	if g.db is not None:
# 		g.db = init_db()

# @app.teardown_request
# def teardown_request(exception):
#     db = getattr(g, 'db', None)
#     if db is not None:
#         db.close()


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
<<<<<<< HEAD
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
=======
		pass_hash = brypt.generate_password_hash(attempted_password)
		new_user = User.create(username = attempted_username, password = pass_hash)

		return jsonify({"response": new_user})
	else:
		return render_template('signup.html')
def login():
	if request_method == 'POST'
		if valid_login(reqest.form['username'], request.form['password']):
			return jsonify({"response": True})
		else:
			response = {
				'response': False,
				'error':  "invalid username/password"
			}
			return jsonify(response)
def valid_login(attempted_username, attempted_password):
	try:
		user = User.get(User.username == attempted_username)
	except UserDoesNotExist:
		response = {
			'response': False,
			'error': "invalid username/password"
		}
		return jsonify(response)
	if user.password == attempted_password:
		return jsonify({'response': True})
>>>>>>> 085dc48498948aa86c64e23e3a12d39f45f63fac
