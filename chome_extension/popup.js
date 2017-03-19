var username = undefined;
var password = undefined;
var storeurl = undefined;

$(document).ready(function () {
	console.log("im ready!");
	chrome.tabs.getSelected(null, function(tab) {
		storeurl = tab.url;
		console.log(storeurl);
	})
})

document.getElementById("login").addEventListener("click", function() {
    /* Validations go here */
    username = document.getElementById("username").value;
    password = document.getElementById("password").value;
    console.log(storeurl);
    $.ajax
    (
        {
            type: "POST",
            url: "http://localhost/contourdb/script.php",
            dataType:"text",
            data: 
            {               
                username: username,
                password: password,
                storeurl: storeurl
            },
            success: function(res)
            {
                console.log(res.length);
                if (res.length != 197) {
                	document.getElementById("login").remove();
                }
                document.getElementById("content").innerHTML =  res;
            }//end function
        }
    );
});
