from flask import Flask, request, jsonify
from flask import render_template
app = Flask(__name__)




@app.route("/")
def index_route():
	return render_template('index.html')

@app.route("/signup", methods=['GET', 'POST'])
def sign_up():
	if request.method == 'POST':
		# get username and password
		#hash password
		#enter user in database
		#return {'response': True} from function
		return jsonify({"randi": "bosdike"})
	else:
		return render_template('signup.html')
