<?php
require_once('conf.php');

function mirrorFiles()
{
	$files = array();
	foreach(glob(MIRROR_DIR.'*') as $file)
		$files[] = basename($file);
	return $files;
}

function selectedFile()
{
	if(!isset($_GET['file']))
		return false;
	$select = $_GET['file'];
	
	$files = mirrorFiles();
	$idx = array_search($select, $files);
	if($idx !== false)
		return $files[$idx];
	return false;
}

function mirrorLinks($file)
{
	$links = array(dirname($HTTP_SERVER_VARS['SCRIPT_URI']).MIRROR_DIR.$file);
	$mirrors = file('mirrors.list');
	foreach($mirrors as $mirror)
		$links[] = $mirror.MIRROR_DIR.$file;
	return $links;
}
