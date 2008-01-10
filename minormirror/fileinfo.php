<?php
require_once 'conf.php';

function downloadFiles()
{
	$files = array();
	//Hard code, remove source PHP files for security
	foreach(glob(MM_DOWNLOADS_DIR.'*') as $file)
		if(preg_match('/\.php$/', $file) == 0)
			$files[] = basename($file);
	return $files;
}

//Return the file that was selected, making sure it's a valid download/file
function GETFile($fieldname = false)
{
	if($fieldname === false)
		$fieldname = 'file';
	if(!isset($_GET[$fieldname]))
		return false;
	$select = $_GET[$fieldname];
	
	$files = downloadFiles();
	$idx = array_search($select, $files);
	if($idx !== false)
		return $files[$idx];
	return false;
}
function getMirrorsFor($url)
{
	if(!file_exists('mirrors.list'))
		return array();
	$mirrors = file('mirrors.list');
	$fname = basename($url);
	$urls = array();
	foreach($mirrors as $mirror)
	{
		if(substr($mirror, -1) == '/')
			$urls[] = $mirror.basename($url);
		else if($fname == basename($mirror))
			$urls[] = $mirror;
	}
	return $urls;
}
function hasHash($file, $type)
{
	//Check if we have the hash on file
	return file_exists(MM_META_DIR.$file.'.'.$type);
}

//File information functions
function getDownloadInfo($file)
{
	//Return information about the download
	$dinfo = array('name' => $file, 'url' => MM_HTTP_ROOT.MM_DOWNLOADS_DIR.basename($file));
	//If metalink, add the url
	if(file_exists(MM_META_DIR. $file.'.metalink'))
		$dinfo['metalinkurl'] = MM_HTTP_ROOT.MM_META_DIR.basename($file).'.metalink';
	$dinfo['mirrors'] = getMirrorsFor($dinfo['url']);
	//TOD Add metlink download information
	//$dinfo['metalinkurl'] = metalinkurl
	return $dinfo;
}

function globDownloadInfoExcluding($glob, $excluded)
{
	$candidates = glob($glob);
	$files = array();
	foreach($candidates as $file)
	{
		$file = basename($file);//Currently, no subdirectories are supported.
		foreach($excluded as $p)
		{
			if(preg_match($p, $file))
				break;
			else
			{
				//Not excluded, get the information
				$files[] = getDownloadInfo($file);
			}
		}
	}
	return $files;
}
