<?php
echo var_dump($_POST);
$db = pg_connect("host=localhost dbname=contour user=allanmeng");
$query = "insert into purchase_rating (user_id, store_id, size_bought, fit_preference, bought_fit_rating, comments) values (" . $_POST["user_id"] . ", " . $_POST["store_id"] . ", '" . $_POST["size_bought"] . "', '" . $_POST["fit_preference"] . "', '" . $_POST["bought_fit_rating"] . "', '" . $_POST["comments"] . "');";
$result = pg_query($db, $query);
?>