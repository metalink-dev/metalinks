<?php
require_once 'conf.php';
require_once 'fileinfo.php';

foreach(array('MM_HTTP_ROOT', 'MM_DOWNLOADS_DIR', 'MM_META_DIR') as $v)
	if(!defined($v))
		die('Depending on undefined predefined');

//Check login
session_start();

$user = (isset($_POST['user']) ? $_POST['user'] : '');
$pass = (isset($_POST['pass']) ? $_POST['pass'] : '');

$valid = false;


if($_SESSION['MM_KEY'] == sha1('bgzBgU7S'.$_SESSION['MM_USER'].$_SERVER['REMOTE_HOST'].'y3Asg0f2'))
	$valid = true;
else if(isset($MM_USERS[$user]) && $pass == $MM_USERS[$user])
{
	//Login with pass and username
	$_SESSION['MM_KEY'] = sha1('bgzBgU7S'.$user.$_SERVER['REMOTE_HOST'].'y3Asg0f2');
	$_SESSION['MM_USER'] = $user;
	$valid = true;
}

if(!$valid)
{
	//Show login form
	header('Location:  '.MM_HTTP_ROOT.'login.php');
	die('Redirect');
}


//If you ask to metalink something
$file = GETFile('metalink');
if($file)
{
	define('INCLUDED BY MINORMIRROR', true);
	require 'metalink.php';
	//BIG BIG BIG TODO HERE!!!!!
	//General idea:
	$dinfo = getDownloadInfo($file);
	
	//Find list of mirrors for this file:
	$urls = $dinfo['mirrors'];

	//Add the default file url, if this root host is also a mirror
	$urls[] = $dinfo['url'];

	// Any link in the mirror.list file ending in '/' is considered a directory mirror (all files)
	// Any link ending in a filename, should have the same basename to be a mirror.
	//Creat metalink
	$metafile = new Metalink();
	foreach($urls as $url)
		$metafile->add_url($url);
	
	$metalink = 'NOT GENERATED YET, CHECK THE CODE!!!!';
	//Write to file
	file_put_contents(MM_META_DIR.$file.'.metalink', $metalink);
}
//Show list of metalinks and allow for metalink creation.
$files = globDownloadInfoExcluding(MM_DOWNLOADS_DIR.'*', array('/.php$/'));
echo '<pre>';
print_r($files);
echo '</pref>';
foreach($files as $file)
{
	$filename = htmlentities($file['name']);
	
	echo '<h4>'.$filename.'</h4>';
	//TODO Change this link into a form which allows you to set the description etc.
	echo '<a href="?metalink='.$filename.'">metalink it</a>';
	echo '<hr>';
}
