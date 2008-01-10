<?php
require 'conf.php';

?>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html; charset=UTF-8" http-equiv="content-type">
	<meta name="dc.creator" content="minormirror" />
	<meta name="language" content="en" />
	<meta name="dc.modified" content="2008-01-08" />
	<meta name="author" content="minormirror" />
	<meta name="lang" content="en" />
	<meta name="copyright" content="Copyright (C) <?php echo MM_PROJECTNAME ?>" />

  <title><?php echo MM_PROJECTNAME ?> administration login</title>
<style type="text/css">
body {
	font-family: 'Bitstream Vera Sans', Verdana, sans-serif;
	margin-left: 25%;
	width: 50%;
}
</style>
<body>
<form action="admin.php" method="post">
	Username <input type="text" name="user"> <br />
	Pass <input type="text" name="pass"> <br />
	<input type="submit">
</form>
</body>
</html>
