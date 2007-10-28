<?php
require_once "inc/file.php";

$files = mirrorFiles();

foreach($files as $file)
{
	echo $file . ': <a href="hash.php?type=md5&amp;file='.$file.'">md5</a> <a href="hash.php?type=sha1&amp;file='.$file.'">sha1</a><br />';
}
