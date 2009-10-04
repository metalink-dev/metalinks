<?php
########################################################################
#
# Project: Metalink
# URL: https://sourceforge.net/projects/metalinks/
# E-mail: webmaster@nabber.org
#
# Copyright: (C) 2008-2009, Neil McNab
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

include_once("convert.php");

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

  if (isset($_GET['url'])) {
    $url = $_GET['url'];

    $curl = new curl();
    $lines = $curl->getFile($url, 1000, 1000);
    if ($lines == FALSE) {
        print "error";
        return array("", "");
    }
  }

  if (isset($_POST['data'])) {
    $lines = $_POST['data'];
  }

  if (isset($lines)) {

    $ver = intval($_REQUEST['v']);

    header('Content-type: application/xml');

    $v4 = stristr($lines, "urn:ietf:params:xml:ns:metalink") !== FALSE;
    if ($v4 AND ($ver == 3)) {
        $lines = metalink4to3($lines);
    } elseif(!$v4 AND $ver == 4) {
        $lines = metalink3to4($lines);
    }

    $lines = split("\n", $lines);

    $i = 0;
    foreach ($lines as $line) {
            echo $line . "\n";
            if ($i == 0) {
                print "<?xml-stylesheet type='text/xsl' href='metalink.xsl'?>\n";
            }
            $i++;
    }
  } else {

?>

<html>
<head>
</head>
<body>

<p><img src="metalink_logo_small.png" alt="Metalink Logo" /></p>
<p>Convert a Metalink file to a HTML web page and convert between v3 and v4.
</p>
<form action="" method="get">
    <p>
      Metalink URL: <input maxlength="500" name="url" size="50" value="" /><input type="submit" />
    <br />
    Output Metalink Version*: <input type="radio" name="v" value="3" checked="checked">3 <input type="radio" name="v" value="4">4
</p>
</form>

<hr />
<form action="" method="post">
    <p>
      Metalink Document XML Text: <br /><textarea rows="20" cols="80" name="data"></textarea>
    <br />
    Output Metalink Version*: <input type="radio" name="v" value="3" checked="checked">3 <input type="radio" name="v" value="4">4
   <br />
<input type="submit" />
</p>
</form>

<p>* This is not a complete conversion, but suitable for download programs.</p>

<p><a href="metalink.xsl">Metalink XML to XHTML XSL</a> - <a href="metalink.3to4.xsl">Metalink 3 to 4 XSL</a> - <a href="metalink.4to3.xsl">Metalink 4 to 3 XSL</a></p>

</body>
</html>

<?php
  }
?>
