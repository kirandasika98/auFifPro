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