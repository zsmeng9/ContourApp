<?php
$db = pg_connect("host=localhost dbname=contour user=allanmeng");
$query = "select * from users where username = '" . $_POST["username"] . "' and password = '" . $_POST["password"] . "'";
$result = pg_query($db, $query);
if (pg_num_rows($result) == 0) {
	echo '<h2> Login Failed </h2>
	<h3> Sign In to your Contour Account </h3>
    <input type="text" id="username" placeholder="Username"><br>
    <input type="text" id="password" placeholder="Password"><br>';
	exit;
} else {
	$html = file_get_contents($_POST["storeurl"]);
	// Get store name
	$doc = new DOMDocument();
	@$doc->loadHTML($html);

	$metas = $doc->getElementsByTagName('meta');

	for ($i = 0; $i < $metas->length; $i++)
	{
	    $meta = $metas->item($i);
	    if($meta->getAttribute('property') == 'og:site_name')
	        $storename = $meta->getAttribute('content');
	}

	$querystoreid = "select id from stores where name='" . $storename ."'";
	$resultsstoreid = pg_query($db, $querystoreid);
	$store_id = pg_fetch_all($resultsstoreid)[0]["id"];


	// Get user measurements
	$user_id = pg_fetch_result($result, 0, "id" );
	$query2 = "select neck, chest, waist from user_sizes where user_id=" . $user_id . "order by timestamp desc limit 1";
	$result2 = pg_query($db, $query2);
	$user_size = pg_fetch_all($result2);

	// Get store size for user
	$queryneck = "select size from store_sizes where neckmin <= " . round($user_size[0]["neck"],0) . " and neckmax >= " . round($user_size[0]["neck"], 0);
	$querychest = "select size from store_sizes where chestmin <= " . round($user_size[0]["chest"],0) . "and chestmax >= " . round($user_size[0]["chest"], 0);
	$querywaist = "select size from store_sizes where waistmin <= " . round($user_size[0]["waist"],0) . "and waistmax >= " . round($user_size[0]["waist"], 0);

	$resultneck = pg_query($db, $queryneck);
	$resultchest = pg_query($db, $querychest);
	$resultwaist = pg_query($db, $querywaist);
	$neck_sizing = pg_fetch_all($resultneck);
	$chest_sizing = pg_fetch_all($resultchest);
	$waist_sizing = pg_fetch_all($resultwaist);

	$storenamearray = array("J.Crew");

	$reviewcountquery = "select count(*) as count from purchase_rating where store_id=" . $store_id;
	$resultreviewcount = pg_query($db, $reviewcountquery);
	$review_count = pg_fetch_all($resultreviewcount)[0]["count"];

	if (in_array ($storename, $storenamearray)) {
		echo "<h2>Welcome " . $_POST["username"] . "</h2>
		<h3>Enjoy shopping with confidence at " . $storename . "</h3><br>
		<li>Neck :" . $user_size[0]["neck"] . " Recommended Size: " . $neck_sizing[0]["size"] . "</li>
		<li>Chest :" . $user_size[0]["chest"] . " Recommended Size: " . $chest_sizing[0]["size"] . "</li>
		<li>Waist :" . $user_size[0]["waist"] . " Recommended Size: " . $waist_sizing[0]["size"] . "</li>
		<h3>Contour Customer Fit Reviews</h3>
		<input type='hidden' id='user_id' value=" . $user_id . ">
		<input type='hidden' id='store_id' value=" . $store_id . ">
		<input type='text' id='size_bought' placeholder='Size Bought'><br>
		<input type='text' id='fit_preference' placeholder='Fit Preference'><br>
		<input type='text' id='bought_fit_rating' placeholder='Rating'><br>
		<input type='text' id='comments' placeholder='Comments'><br>
		<button id='submit_review'>Submit Review</button>
		<button id='view_reviews'>View Reviews (" . $review_count . ")</button>";
	}
}
?>
