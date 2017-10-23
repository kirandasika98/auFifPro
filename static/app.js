function signupUser() {
	var username = $('#userName').val();
	var password = $('#userPassword').val();
	var verifyPassword = $("#verifyUserPassword").val();
	var payloadData = {
		'username': username,
		'password': password,
		'verify_password': verifyPassword
	};
	//Send post request to /signup
	$.post($SCRIPT_ROOT + "/signup", payloadData, function(data, status){
        if (data.response) {
        	window.location.replace($SCRIPT_ROOT + "/dashboard");
        }
        else {
        	document.getElementById('error').innerHTML = data.error;
        }
    });
}

function loginUser() {
	var username = $('#userName').val();
	var password = $('#userPassword').val();
	var payloadData = {
		'username': username,
		'password': password
	};

	$.post($SCRIPT_ROOT + "/", payloadData, function(data, status) {
		if (data.response == true) {
			window.location.replace($SCRIPT_ROOT + "/dashboard");
		}
		else {
			document.getElementById('error').innerHTML = data.error;
		}
	});
}

function newMatch() {
	var player1_id = $("#player_1_dropdown").val();
	var player2_id = $("#player_2_dropdown").val();
	var player1_goals = $("#player_1_goals").val();
	var player_2_goals = $("#player_2_goals").val();
	
	var payloadData = {
		'player1_id': player1_id,
		'player2_id': player2_id,
		'player1_goals': player1_goals,
		'player2_goals': player_2_goals
	};

	$.post($SCRIPT_ROOT + "/new_match", payloadData, function(data, status){
		if (data.response == true) {
			$('#myModal').modal('hide');
			document.getElementById("refresh_helper").innerHTML = "<a href='/dashboard'>Refresh</a>";
		}
		else {
			document.getElementById("new_match_error").innerHTML = "<font color='red'>" + data.error + "</font>";
		}
	});
}
