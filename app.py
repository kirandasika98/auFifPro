import bmemcached
import os
import json
from flask import Flask, request, jsonify, g
from flask import render_template
from flask import make_response, redirect
from flask_bcrypt import Bcrypt
from models import User, Match, db, CachedYelpPlace, Wager
from peewee import IntegrityError, DoesNotExist
from ranking import calculate_ranks
from datetime import datetime, timedelta
from profile_matches import get_my_matches
from utils import MyMemcache
from yelp import YelpFusionHandler

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Memcache Setup
if "HEROKU" not in os.environ:
    # Get from credentials file
    memcache_credentials = json.loads(file("credentials.json")
                                      .read())["memcache"]
    mc = bmemcached.Client(memcache_credentials["host"],
                           memcache_credentials["username"],
                           memcache_credentials["password"])
    pass
else:
    # Get data from Heroku
    mc = bmemcached.Client(os.environ["MEMCACHE_HOST"],
                           os.environ["MEMCACHE_USERNAME"],
                           os.environ["MEMCACHE_PASSWORD"])
memcache = MyMemcache(mc)

# Cookie expiry
sixty_days = datetime.now() + timedelta(days=60)

# Memcache key expiry
TWENTY_MIN = 600


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
            # set cookie
            response = make_response(jsonify({"response": True}))
            # setting a cookie hash
            response.set_cookie("username", request.form['username'],
                                expires=sixty_days)
            return response
        else:
            response = {
                'response': False,
                'error': "invalid username/password"
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
    user = User.get(username=request.cookies['username'])
    usernames = {}
    for user1 in User.select():
        usernames[user1.get_id()] = user1.username

    # Check if ranks have to be updated and ranks are there in memcache
    # Update ranks if needed and set update_ranks to False

    # Defining a rankings variable to hold the OrderedDict of ranks
    rankings = None
    # Bool representing whether we have to update the ranks
    update_ranks = mc.get("update_ranks")
    # An Object to represent the ranks to be displayed
    ranks = mc.get("ranks")

    if update_ranks is not None and update_ranks is False:
        # Return ranks as they are the most recent ones
        print "Getting ranks from memcache..."
        rankings = ranks

    elif update_ranks is None or update_ranks is True:
        print "Calculating new ranks"
        # Calculating new ranks
        rankings = calculate_ranks()
        # Updating memcache with the recent ranks and update_ranks to False
        mc.set("ranks", rankings)
        mc.set("update_ranks", False)

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

        if player1_id == player2_id:
            return jsonify({"response": False, "error": "Player 1 cannot be the same as Player2"})

        Match.create(player1_id=player1_id, player2_id=player2_id,
                     player1_goals=player1_goals, player2_goals=player2_goals)

        # ranks in memcache now are obselete so update the 'update_ranks' key
        mc.set("update_ranks", True)

        return jsonify({"response": True})


@app.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form["userName"]
        password = request.form["userPassword"]
        verify_password = request.form["verifyPassword"]
        try:
            user = User.get(User.username == username)
        except DoesNotExist:
            return render_template("forgot_password.html", password_info="User does not exist")

        if password == verify_password:
            user.password = bcrypt.generate_password_hash(password)
            user.save()
            return redirect("/")
        else:
            return render_template("forgot_password.html", password_info="Password's dont match.")

    return render_template('forgot_password.html')


@app.route("/profile/<id>", methods=['GET'])
def profile(id=None):
    if "username" in request.cookies:
        user = User.get(User.id == id)
        outcomes = get_my_matches(user)
        return render_template("profile.html", user=user, outcomes=outcomes)
    return redirect("/")


@app.route("/wagers", methods=['GET', 'POST'])
def wagers():
    if "username" not in request.cookies:
        return redirect("/")

    if request.method == 'POST':
        # Getting wager initiator
        initiator = User.get(User.username == request.cookies['username'])
        # Check if wager is with same user
        if initiator.id == int(request.form['user']):
            return jsonify({"response": False, "error": "Choose a different player."})

        # Creating a new CachedYelpPlace instance to check if we already have it
        try:
            yelp_business = CachedYelpPlace.create(yelp_id=request.form['id'],
                                            yelp_data=request.form['name'])
        except IntegrityError:
            # Yelp business already exists in the database
            yelp_business = CachedYelpPlace.get(CachedYelpPlace.yelp_id == request.form['id'])

        # Creating new Wager
        wager = Wager.create(initiator_id=initiator.get_id(),
                             opponent_id=int(request.form['user']),
                             yelp_id_id=yelp_business.get_id())
        # Success response for new wager
        return jsonify({"response": True, "id": wager.get_id()})

    # Retrieving an instance of the current user
    curr_user = User.get(User.username == request.cookies['username'])
    users = User.select()
    # Selecting wagers that the user is participating in
    wagers = Wager.select().where((Wager.initiator == curr_user.get_id()) |
                                  (Wager.opponent == curr_user.get_id()))
    # Default response for GET request
    return render_template("wager.html", name=request.cookies['username'],
                           users=users,
                           wagers=wagers)


@app.route("/wager_result/<wager_id>", methods=['GET', 'POST'])
def wager_result(wager_id=None):
    """
    Updates the database with the wager result
    :return: HttpResponse
    """
    if "username" not in request.cookies:
        return redirect("/")

    if request.method == 'POST':
        # Add the new match in the database and update the wager
        # With the new match id
        wager_match = Match.create(player1_id=request.form['player1_id'],
                                   player2_id=request.form['player2_id'],
                                   player1_goals=request.form['player1_goals'],
                                   player2_goals=request.form['player2_goals'])
        # Updating wager with the match
        wager = Wager.get(Wager.id == wager_id)
        wager.match = wager_match
        wager.save()

        # Update memcache key
        mc.set("update_ranks", True)
        return jsonify({"response": True})

    wager = Wager.get(Wager.id == wager_id)
    return render_template("wager_result.html", name=request.cookies['username'],
                           player1=wager.initiator, player2=wager.opponent)


@app.route("/yelp_autocomplete", methods=['POST'])
def yelp_autocomplete():
    query = request.form.get('query')
    # Use the Yelp api hander to send the information and get back new information
    yfh = YelpFusionHandler()
    return jsonify(yfh.get_auto_complete_businesses({"text": query}))


if __name__ == "__main__":
    app.run(debug=True)
