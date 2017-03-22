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

$(document).on('click','#submit_review',function() {
    /* Validations go here */
    user_id = document.getElementById("user_id").value;
    store_id = document.getElementById("store_id").value;
    size_bought = document.getElementById("size_bought").value;
    fit_preference = document.getElementById("fit_preference").value;
    bought_fit_rating = document.getElementById("bought_fit_rating").value;
    comments = document.getElementById("comments").value;

    $.ajax
    (
        {
            type: "POST",
            url: "http://localhost/contourdb/submitreview.php",
            dataType:"text",
            data: 
            {               
                user_id: user_id,
                store_id: store_id,
                size_bought: size_bought,
                fit_preference: fit_preference,
                bought_fit_rating: bought_fit_rating,
                comments: comments
            },
            success: function(res)
            {
                console.log(res);
                document.getElementById("review_content").innerHTML =  res;
            }//end function
        }
    );
});

$(document).on('click','#view_reviews',function() {
    store_id = document.getElementById("store_id").value;

    $.ajax
    (
        {
            type: "POST",
            url: "http://localhost/contourdb/viewreviews.php",
            dataType:"text",
            data: 
            {               
                store_id: store_id
            },
            success: function(res)
            {
                console.log(res);
                var url = "data:text/html," + encodeURIComponent(res);
                chrome.tabs.create({url: url});
            }//end function
        }
    );
});
