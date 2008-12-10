<?php
########################################################################
#
# Project: Metalink
# URL: https://sourceforge.net/projects/metalinks/
# E-mail: webmaster@nabber.org
#
# Copyright: (C) 2008, Neil McNab
# License: GNU General Public License Version 2
#   (http://www.gnu.org/copyleft/gpl.html)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# Filename: $URL: index.php $
# Last Updated: $Date December 9, 2008 $
# Author(s): Neil McNab
#
# Description:
#   Decodes a metalink url into a html file.  Requires curl.
#
########################################################################

class curl {
  var $timeout;
  var $waittimeout;
  var $url;
  var $file_contents = "";
  function getFile($url,$timeout=5000,$waittimeout=10000) {
    # use CURL library to fetch remote file
    $ch = curl_init();
    $this->url = $url;
    $this->timeout = $timeout;
    $this->waittimeout = $waittimeout;
    curl_setopt ($ch, CURLOPT_URL, $this->url);
//    curl_setopt ($ch, CURLOPT_FOLLOWLOCATION, TRUE);
//    curl_setopt ($ch, CURLOPT_MAXREDIRS, 10);
    curl_setopt ($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt ($ch, CURLOPT_CONNECTTIMEOUT_MS, $this->timeout);
    curl_setopt ($ch, CURLOPT_TIMEOUT_MS, $this->waittimeout);
    //curl_setopt ($ch, CURLOPT_WRITEFUNCTION, '$this->read');
    //curl_setopt ($ch, CURLOPT_LOW_SPEED_LIMIT, 10000000);
    //curl_setopt ($ch, CURLOPT_LOW_SPEED_TIME, 1);
    $this->file_contents = curl_exec($ch);
    //curl_exec($ch);
    if ( curl_getinfo($ch,CURLINFO_HTTP_CODE) !== 200 ) {
      return('Bad Data File '.$this->url . " " . curl_getinfo($ch,CURLINFO_HTTP_CODE));
    } else {
      return $this->file_contents;
    }
  }
  function read($ch, $string) {
    $length = strlen($string);
    $this->file_contents .= $string;
    echo "Received $length bytes<br />\n";
    return $length;
  }
}


    $url = $_GET['url'];

    header('Content-type: application/xml');

    $curl = new curl();
    $lines = $curl->getFile($url, 1000, 1000);
    if ($lines == FALSE) {
        print "error";
        return array("", "");
    }
    $lines = split("\n", $lines);

    $i = 0;
    foreach ($lines as $line) {
            echo $line;
            if ($i == 0) {
                print "<?xml-stylesheet type='text/xsl' href='metalink.xsl'?>\n";
            }
            $i++;
    }

?>
