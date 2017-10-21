function loginUser() {
	var userName = $('#userName').val();
	var password = $('#userPassword').val();

	//Send post request to /signup
	$.post($SCRIPT_ROOT + "/signup", function(data, status){
        console.log("Data: " + data + "\nStatus: " + status);
    });
}