<?php
$db = pg_connect("host=localhost dbname=contour user=allanmeng");
$query = "select id, store_id, size_bought, fit_preference, bought_fit_rating, comments, user_id from purchase_rating where store_id=" . $_POST["store_id"] . ";";
$result = pg_query($db, $query);
$reviews = pg_fetch_all($result);
$titlecount = 0;
echo '<script src="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>
<link rel="stylesheet" type="text/css" href="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">';
echo "<table class='table'>
<thead>
<style>
table, th, td {
   border: 1px solid black;
}
</style>";

foreach ($reviews as $review) {
	echo "<tr>";
	if ($titlecount == 0) {
		foreach ($review as $column => $value) {
			echo "<th>" . $column . "</th>";
		}
		echo "</tr></thead><tbody>";
		echo "<tr>";
		$titlecount = $titlecount + 1;
	}

	foreach ($review as $column => $value) {
		echo "<td>" . $value . "</td>";
	}
	echo "</tr>";
}
echo "</tbody>";
echo "</table>";
?>