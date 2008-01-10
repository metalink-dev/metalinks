<?php
define(MM_HTTP_ROOT, 'http://example.com/');//This should be configured to a complete http:// root, ending in /
define(MM_PROJECTNAME, 'ExampleProject');
define(MM_DOWNLOADS_DIR, 'downloads/');//Download directory, with slash.
define(MM_META_DIR, 'meta/');//Meta data directory, with slash.

$MM_HASHES = explode(' ', 'md5 sha1');//Supported digests.
$MM_USERS = array('admin' => 'admin');//User password information.

