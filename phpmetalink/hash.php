<?php
require_once 'conf.php';
require_once 'inc/file.php';

$file = selectedFile();

if(!$file)
	die("Need to select a file to hash it");
$hash = false;

$type = false;
if($_GET['type'] == 'md5')
	$type = 'md5';
if($_GET['type'] == 'sha1')
	$type = 'sha1';

if(!$type)
	die('could not determine hash');

//$type SAFE now

if(hasHash($file, $type))
	die('Already have that hash, remove the cache before rerunning this');

if($type == 'md5')
	$hash = md5_file(MIRROR_DIR.$file);
if($type == 'sha1')
	$hash = sha1_file(MIRROR_DIR.$file);

if(!$hash)
	die('could not create hash');

file_put_contents(META_DIR.$file.'.'.$type, $hash);

echo "Done!";
