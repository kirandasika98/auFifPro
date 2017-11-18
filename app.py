"""
All app views in this file.
"""
import os
import json
import time
from datetime import datetime, timedelta
import bmemcached
from flask import Flask, request, jsonify, g
from flask import render_template
from flask import make_response, redirect
from flask_bcrypt import Bcrypt
from models import User, Match, db, CachedYelpPlace, Wager
from peewee import IntegrityError, DoesNotExist
from ranking import calculate_ranks
from profile_matches import get_my_matches
from yelp import YelpFusionHandler

app = Flask(__name__)
BCRYPT = Bcrypt(app)

# Memcache Setup
if "HEROKU" not in os.environ:
    # Get from credentials file
    MEMCACHE_CREDENTIALS = json.loads(file("credentials.json")
                                      .read())["memcache"]
    MC = bmemcached.Client(MEMCACHE_CREDENTIALS["host"],
                           MEMCACHE_CREDENTIALS["username"],
                           MEMCACHE_CREDENTIALS["password"])
else:
    # Get data from Heroku
    MC = bmemcached.Client(os.environ["MEMCACHE_HOST"],
                           os.environ["MEMCACHE_USERNAME"],
                           os.environ["MEMCACHE_PASSWORD"])

# Cookie expiry
SIXTY_DAYS = datetime.now() + timedelta(days=60)

# Memcache key expiry
TWENTY_MIN = 600


@app.before_request
def before_request():
    """
    runs before any flask request
    """
    g.db = db
    g.db.connect()


@app.teardown_request
def teardown_request(response):
    """
    closes database connection for current request
    """
    g.db.close()
    return response


@app.after_request
def after_request(response):
    """
    closes database connection for current request
    """
    g.db.close()
    return response


@app.route("/", methods=['GET', 'POST'])
def index_route():
    """
    index route for the app
    """
    if request.method == 'POST':
        if valid_login(request.form['username'], request.form['password']):
            # set cookie
            response = make_response(jsonify({"response": True}))
            # setting a cookie hash
            response.set_cookie("username", request.form['username'],
                                expires=SIXTY_DAYS)
            return response

        response = {
            'response': False,
            'error': "invalid username/password"
        }
        return jsonify(response)

    if "username" in request.cookies:
        return redirect("/dashboard")

    return render_template('index.html')


def valid_login(attempted_username, attempted_password):
    """
    Helper function to check if a login is valid.
    """
    try:
        user = User.get(User.username == attempted_username)
    except DoesNotExist:
        return False
    return BCRYPT.check_password_hash(user.password, attempted_password)


@app.route("/logout")
def logout():
    """
    this view does all nescessary stuff for user logout.
    """
    if "username" in request.cookies:
        response = make_response(redirect("/"))
        response.set_cookie("username", "", expires=0)
        return response
    return redirect("/dashboard")


@app.route("/signup", methods=['GET', 'POST'])
def sign_up():
    """
    Getting username and password
    hashing password and creating a database entry and
    returning true or returning to signup page
    """
    if request.method == 'POST':
        attempted_username = request.form['username']
        attempted_password = request.form['password']
        attempted_verified = request.form['verify_password']

        if attempted_password != attempted_verified:
            return jsonify({"response": False, "error": "Your password did not match"})

        if len(attempted_username) < 1 or len(attempted_password) < 1:
            return jsonify({"response": False, "error": "please provide a username/password"})

        pass_hash = BCRYPT.generate_password_hash(attempted_password)

        try:
            User.create(username=attempted_username, password=pass_hash)
        except IntegrityError:
            return jsonify({"response": False, "error": "username already taken"})

        # set cookie and return
        response = make_response(jsonify({"response": True}))
        response.set_cookie("username", attempted_username, expires=SIXTY_DAYS)
        return response
    else:
        return render_template('signup.html')


@app.route("/dashboard")
def dashboard():
    """
    dashboard view
    """
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
    update_ranks = MC.get("update_ranks")
    # An Object to represent the ranks to be displayed
    ranks = MC.get("ranks")

    if update_ranks is not None and update_ranks is False:
        # Return ranks as they are the most recent ones
        print "Getting ranks from memcache..."
        rankings = ranks

    elif update_ranks is None or update_ranks is True:
        print "Calculating new ranks"
        # Calculating new ranks
        rankings = calculate_ranks()
        # Updating memcache with the recent ranks and update_ranks to False
        MC.set("ranks", rankings)
        MC.set("update_ranks", False)

    return render_template("dashboard.html", name=request.cookies['username'],
                           is_moderater=user.is_moderater,
                           usernames=usernames,
                           rankings=rankings)


@app.route("/new_match", methods=['GET', 'POST'])
def new_match():
    """
    async request from client to create a new match
    """
    if request.method == 'POST':
        player1_id = request.form['player1_id']
        player2_id = request.form['player2_id']

        # Checking to see if goals were provided
        try:
            player1_goals = int(request.form['player1_goals'])
            player2_goals = int(request.form['player2_goals'])
        except ValueError:
            return jsonify({"response": False, "error": "Provide goals for players."})

        if player1_id == player2_id:
            return jsonify({"response": False, "error": "Player 1 cannot be the same as Player2"})

        Match.create(player1_id=player1_id, player2_id=player2_id,
                     player1_goals=player1_goals, player2_goals=player2_goals)

        # ranks in memcache now are obselete so update the 'update_ranks' key
        MC.set("update_ranks", True)

        return jsonify({"response": True})


@app.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    """
    allows user to reset password
    """
    if request.method == 'POST':
        username = request.form["userName"]
        password = request.form["userPassword"]
        verify_password = request.form["verifyPassword"]
        try:
            user = User.get(User.username == username)
        except DoesNotExist:
            return render_template("forgot_password.html", password_info="User does not exist")

        if password == verify_password:
            user.password = BCRYPT.generate_password_hash(password)
            user.save()
            return redirect("/")

        return render_template("forgot_password.html", password_info="Password's dont match.")

    return render_template('forgot_password.html')


@app.route("/profile/<pid>", methods=['GET'])
def profile(pid=None):
    """
    Displays user profile page.
    """
    if "username" in request.cookies:
        user = User.get(User.id == pid)
        outcomes = get_my_matches(user)
        return render_template("profile.html", user=user, outcomes=outcomes,
                               name=request.cookies['username'])
    return redirect("/")


@app.route("/wagers", methods=['GET', 'POST'])
def wagers():
    """
    Either displayes new wager or gives an option to
    create a new wager.
    """
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
    user_wagers = Wager.select().where((Wager.initiator == curr_user.get_id()) |
                                       (Wager.opponent == curr_user.get_id()))
    # Default response for GET request
    return render_template("wager.html", name=request.cookies['username'],
                           users=users,
                           wagers=user_wagers)


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
        MC.set("update_ranks", True)
        return jsonify({"response": True})

    wager = Wager.get(Wager.id == wager_id)
    return render_template("wager_result.html", name=request.cookies['username'],
                           player1=wager.initiator, player2=wager.opponent)


@app.route("/yelp_autocomplete", methods=['POST'])
def yelp_autocomplete():
    """
    Queries the yelp autocomplete api for results
    """
    query = request.form.get('query')
    # Use the Yelp api hander to send the information and get back new information
    yfh = YelpFusionHandler()
    return jsonify(yfh.get_auto_complete_businesses({"text": query}))


@app.route("/yelp_detail/<yelp_id>", methods=['GET'])
def yelp_detail(yelp_id):
    """
    Get's more information on a yelp business and caches in memcache.
    """
    # Initialize Yelp Fusion Handler Object
    yfh = YelpFusionHandler()

    # Get Yelp Business data and also cache it in the memcache with expiry
    # Check memcache for data cache associated with current yelp_id
    if MC.get(yelp_id) is None:
        business_data = yfh.get_business_data_by_id(yelp_id=yelp_id)
        # Cache set for 20 min
        MC.set(yelp_id, business_data, time=(int(time.time()) + TWENTY_MIN))
    else:
        # Getting data from cache
        business_data = MC.get(yelp_id)

    return render_template("wager_detail.html",
                           yelp_data=business_data,
                           name=request.cookies['username'])

@app.route("/worker", methods=['POST','GET'])
def worker():
    """
    Worker view for all background tasks that have to be completed
    """
    if request.method == 'POST':
        # Get process type
        # Schedule process on redis queue
        # Return confirmation
        pass

    # Eventually should return a list of all processes scheduled.
    return jsonify({"response": True})

if __name__ == "__main__":
    app.run(debug=True)
