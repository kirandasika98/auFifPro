from flask import Flask, request, jsonify, g
from flask import render_template
from flask import make_response, redirect
from flask_bcrypt import Bcrypt
from models import User, Match, init_db, db
from peewee import IntegrityError, DoesNotExist
from ranking import calculate_ranks
from datetime import datetime, timedelta
from profile_matches import get_my_matches

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Cookie expiry
sixty_days = datetime.now() + timedelta(days=60)

@app.before_request
def before_request():
	g.db = db
	g.db.connect()

@app.teardown_request
def teardown_request(response):
	g.db.close()
	return response

@app.after_request
def after_request(response):
	g.db.close()
	return response


@app.route("/", methods=['GET', 'POST'])
def index_route():
	if request.method == 'POST':
		if valid_login(request.form['username'], request.form['password']):
			#set cookie
			response = make_response(jsonify({"response": True}))
			# setting a cookie hash
			response.set_cookie("username", request.form['username'],
								expires=sixty_days)
			return response
		else:
			response = {
				'response': False,
				'error':  "invalid username/password"
			}
			return jsonify(response)

	if "username" in request.cookies:
		return redirect("/dashboard")

	return render_template('index.html')


def valid_login(attempted_username, attempted_password):
	try:
		user = User.get(User.username == attempted_username)
	except DoesNotExist:
		return False
	return bcrypt.check_password_hash(user.password, attempted_password)


@app.route("/logout")
def logout():
	if "username" in request.cookies:
		response = make_response(redirect("/"))
		response.set_cookie("username", "", expires=0)
		return response
	return redirect("/dashboard")


@app.route("/signup", methods=['GET', 'POST'])
def sign_up():
	if request.method == 'POST':
		"""
		Getting username and password
		hashing password and creating a database entry and
		returning true or returning to signup page
		"""
		attempted_username = request.form['username']
		attempted_password = request.form['password']
		attempted_verified = request.form['verify_password']

		if attempted_password != attempted_verified:
			return jsonify({"response": False, "error": "Your password did not match"})

		if len(attempted_username) < 1 or len(attempted_password) < 1:
			return jsonify({"response": False, "error": "please provide a username/password"})

		pass_hash = bcrypt.generate_password_hash(attempted_password)

		try:
			User.create(username=attempted_username, password=pass_hash)
		except IntegrityError:
			return jsonify({"response": False, "error": "username already taken"})

		# set cookie and return
		response = make_response(jsonify({"response": True}))
		response.set_cookie("username", attempted_username, expires=sixty_days)
		return response
	else:
		return render_template('signup.html')

@app.route("/dashboard")
def dashboard():
	if "username" not in request.cookies:
		return redirect("/")
	user = User.get(username = request.cookies['username'])
	usernames = {}
	for user1 in User.select():
		usernames[user1.get_id()] = user1.username
	rankings = calculate_ranks()
	return render_template("dashboard.html", name=request.cookies['username'],
							is_moderater=user.is_moderater,
							usernames=usernames,
							rankings=rankings)

@app.route("/new_match", methods=['GET', 'POST'])
def new_match():
	if request.method == 'POST':
		player1_id = request.form['player1_id']
		player2_id = request.form['player2_id']

		# Checking to see if goals were provided
		try:
			player1_goals = int(request.form['player1_goals'])
			player2_goals = int(request.form['player2_goals'])
		except:
			return jsonify({"response": False, "error": "Provide goals for players."})

		if (player1_id == player2_id):
			return jsonify({"response": False, "error": "Player 1 cannot be the same as Player2"})

		Match.create(player1_id = player1_id, player2_id = player2_id,
					player1_goals = player1_goals, player2_goals = player2_goals)

		return jsonify({"response": True})

@app.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
	if request.method == 'POST':
		password_info = "email sent successfully"
		return render_template("forgot_password.html", password_info=password_info)

	return render_template('forgot_password.html')


@app.route("/profile/<id>", methods=['GET'])
def profile(id=None):
	if "username" in request.cookies:
		user = User.get(User.id == id)
		outcomes = get_my_matches(user)
		return render_template("profile.html", user=user, outcomes=outcomes)
	return redirect("/")


if __name__ == "__main__":
	app.run(debug=True)
