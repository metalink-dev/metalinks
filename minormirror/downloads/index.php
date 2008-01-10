<?php
require '../fileinfo.php';

//Show an index of the files, add metalinks if we have them.
$files = globDownloadInfoExcluding('./*', array('/.php$/'));

?>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html; charset=UTF-8" http-equiv="content-type">
	<meta name="dc.creator" content="sourcelocation.net" />
	<meta name="language" content="en" />
	<meta name="dc.modified" content="2008-01-08" />
	<meta name="author" content="sourcelocation.net" />
	<meta name="lang" content="en" />
	<meta name="copyright" content="Copyright (C) sourcelocation.net" />

  <title><?php echo MM_PROJECTNAME ?> downloads</title>
<style type="text/css">
body {
	font-family: 'Bitstream Vera Sans', Verdana, sans-serif;
	margin-left: 25%;
	width: 50%;
}
</style>
<body>
<?php
foreach($files as $file)
{
	//Show url to file, if no metalink exists, otherwise show metalink
	if(isset($file['metalinkurl']))
		echo '<a href="'.htmlentities($file['metalink']).'">';
	else
		echo '<a href="'.htmlentities($file['url']).'">';
	
	echo htmlentities($file['name']).'</a>';
	echo '<br>';
}
?>
</body>
</html>
