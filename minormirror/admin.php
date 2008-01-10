<?php

//Check login
session_start();

$user = (isset($_POST['user']) ? $_POST['user'] : '');
$pass = (isset($_POST['pass']) ? $_POST['pass'] : '');

$valid = false;
if($_SESSION['MM_KEY'] == sha1('bgzBgU7S'.$user.$_SERVER['REMOTE_HOST'].'y3Asg0f2'))
	$valid = true;
else if(isset(MM_USER[$user]) && $pass == MM_USER[$user])
{
	//Login with pass and username
	$_SESSION['MM_KEY'] == sha1('bgzBgU7S'.$user.$_SERVER['REMOTE_HOST'].'y3Asg0f2');
}


if(!$valid)
{
	//Show login form
	header('Redirect: '.MM_HTTP_ROOT.'login.html');
	die();
}

//If you ask to metalink something
$metalink = (isset($_GET['metalink']) ? $_GET['metalink'] : false);
if($metalink)
{
	define('INCLUDED BY MINORMIRROR', true);
	require 'metalink.php';
	//BIG BIG BIG TODO HERE!!!!!
	//General idea:
	//Find list of mirrors for this file:
	// Any link in the mirror.list file ending in '/' is considered a directory mirror (all files)
	// Any link ending in a filename, should have the same basename to be a mirror.
	//Creat metalink
	//Write to file
	//file_put_contents(META_DIR.$file.'.metalink', $metalink);
}
//Show list of metalinks and allow for metalink creation.
$files = globDownloadInfoExcluding(MM_DOWNLOADS_DIR.'*', array('/.php$/'));
foreach($filesas as $file)
{
	$filename = htmlentities($file['name']);
	
	echo '<h4>'.$filename.'</h4>';
	//TODO Change this link into a form which allows you to set the description etc.
	echo '<a href="?metalink='.$filename.'">metalink it</a>';
	echo '<hr>';
}
