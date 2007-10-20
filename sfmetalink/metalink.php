<?php
/*
	SFmetalink - Generate a metalink for a list of SF download links
	Copyright (C) 2005  A. Bram Neijt <bram@neijt.nl>

	This program is free software; you can redistribute it and/or
	modify it under the terms of the GNU General Public License
	as published by the Free Software Foundation; either version 2
	of the License, or (at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program; if not, write to the Free Software
	Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
*/

///// Start of configuration
//Alternatively use $downloads = file('filecontainingdownloadlinks.txt');
$project = 'metalinks';
$downloads = array('http://downloads.sourceforge.net/metalinks/metalink_editor-1.1.0.exe');
$use_content_disposition = true;

///// End of configuration

$files = array();
foreach($downloads as $d)
{
	$files[] = basename($d);
}

$filename = isset($_GET['file']) ? $_GET['file'] : false;
$idx = array_search($filename, $files);
if($idx !== false)
	$filename = $files[$idx];
else
  $filename = false;

//Show metalink if we have a target
if($filename)
{
	//Show metalink
	$ml = file_get_contents('sfmetalink.tpl');
	$ml = str_replace('%%FILENAME%%', $filename, $ml);
	$ml = str_replace('%%PROJECT%%', $project, $ml);
	header('Content-type: application/metalink+xml');
	if($use_content_disposition)
		header('Content-Disposition: attachment; filename="'.addslashes($filename).'.metalink"');
	die($ml);
}



//////////////////// Change below to change the listing system/layout




//Default behavior is to list the files
echo '<?xml version="1.0" encoding="UTF-8"?>';
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nl" lang="nl">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<title>sfmetalink example page</title>
</head>
<body>
Files to download with metalink:
<ul>
<?php
foreach($files as $f)
	echo '<li><a href="?file='.urlencode($f).'">'.htmlentities($f).'</a></li>';

?>
</ul>
</body>
</html>

