function signupUser() {
	var userName = $('#userName').val();
	var password = $('#userPassword').val();
	var payloadData = {
		'username': userName,
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