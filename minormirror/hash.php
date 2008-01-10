<?php
require_once 'fileinfo.php';

$file = GETFile();

if(!$file)
	die("Need to select a file to hash it");

//Hash as much hashes that don't exists yet, for the given file.
foreach(MM_HASHES as $type)
{
	if(!hasHash($file, $type))
	{
		//Create the hash
		$hash = false;
		if($type == 'md5')
			$hash = md5_file(MIRROR_DIR.$file);
		if($type == 'sha1')
			$hash = sha1_file(MIRROR_DIR.$file);

		if(!$hash)
			die('could not create hash');		
		file_put_contents(META_DIR.$file.'.'.$type, $hash);
		echo "Created $type hash";
	}
}



