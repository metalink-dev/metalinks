<?php

$url_str = "#URL#                                                                                                                                                                                                                                                          #";
$filename_str = "#FILENAME#                                                                                         #";
$welcome_str = "#WELCOME#                                                                                          #";
$title_str = "#TITLE#                                                                                            #";
$launch_str = "#LAUNCH#";
$launchbtn_str = "#LAUNCHBTN#             #";
$launch_filename_str = "#LAUNCHFILENAME#                                                                                   #";

function new_string($text, $old_str)
{
    $len_new = strlen($text);
    $len_old = strlen($old_str);
    if($len_new == $len_old) {
        return $text;
    }
    elseif($len_new > $len_old) {
        return substr($old_str, 0, $len_old);
    }
    else {
        return str_pad($text, $len_old, "\0");
    }
}

$file = file_get_contents("downloader.exe");

$file = str_replace($url_str, new_string($_POST["url"], $url_str), $file);
$file = str_replace($filename_str, new_string($_POST["filename"], $filename_str), $file);
$file = str_replace($welcome_str, new_string($_POST["welcome"], $welcome_str), $file);
$file = str_replace($title_str, new_string($_POST["title"], $title_str), $file);
$file = str_replace($launch_str, new_string($_POST["launch"], $launch_str), $file);
$file = str_replace($launchbtn_str, new_string($_POST["launchbtn"], $launchbtn_str), $file);
$file = str_replace($launch_filename_str, new_string($_POST["launchfile"], $launch_filename_str), $file);

header('Content-type: application/octet-stream');
header('Content-Disposition: attachment; filename="downloader.exe"');
echo $file;

?>