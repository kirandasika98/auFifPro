function signupUser() {
	var username = $('#userName').val();
	var password = $('#userPassword').val();
	var payloadData = {
		'username': username,
		'password': password
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
			window.location.replace($SCRIPT_ROOT + "/dashboard");
		}
		else {
			console.log('bosri');
		}
	});
}