<?php
require_once "inc/file.php";

$files = mirrorFiles();

foreach($files as $file)
{
	echo $file . ': ';
	if(hasMD5($file))
		echo ' MD5 ';//.MD5For($file);
	else
		echo '<a href="hash.php?type=md5&amp;file='.$file.'">calculate md5</a>';

	if(hasSHA($file))
		echo ' SHA1 ';//.SHA1For($file);
	else
		echo '<a href="hash.php?type=sha1&amp;file='.$file.'">calculate sha1</a>';

	echo '<br />';
}
