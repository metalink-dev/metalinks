#include "Globals.ih"
std::string Globals::stylesheet("\
<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n	\
\n	\
<xsl:stylesheet version=\"1.0\"\n	\
xmlns:m=\"http://metalinks.sourceforge.net\"\n	\
xmlns:xsl=\"http://www.w3.org/1999/XSL/Transform\">\n	\
\n	\
<xsl:output\n	\
  method = \"html\"\n	\
  encoding = \"UTF-8\"\n	\
  indent = \"yes\"\n	\
	/>\n	\
\n	\
<xsl:template \n	\
	match=\"//m:digest[@dtype='gnunet070file']\"\n	\
	>\n	\
	<xsl:variable name=\"link\">gnunet://ecrs/chk/<xsl:value-of select=\"current()\" />.<xsl:value-of select=\"current()/../m:digest[@dtype='gnunet070query']\" />.<xsl:value-of select=\"current()/../../m:size\" /></xsl:variable>\n	\
	<a href=\"{$link}\">Download using GNUnet 0.7.x</a><br />\n	\
</xsl:template>\n	\
\n	\
<xsl:template \n	\
	match=\"//m:digest[@dtype='md5']\"\n	\
	>\n	\
	\n	\
  <xsl:variable name=\"link\">http://bitzi.com/lookup/md5:<xsl:value-of select=\"current()\" /></xsl:variable>\n	\
	<a href=\"{$link}\">Online information by Bitzi.com (using MD5)</a><br />\n	\
	<xsl:text>MD5: </xsl:text>\n	\
	<xsl:value-of select=\"current()\" /><br />\n	\
</xsl:template>\n	\
\n	\
\n	\
<!-- magnet:?xt=urn:sha1:YNCKHTQCWBTRNJIV4WNAE52SJUQCZO5C -->\n	\
<xsl:template \n	\
	match=\"//m:digest[@dtype='sha1']\"\n	\
	>\n	\
	<!-- Simple translation, not really RFC2396 uri escaped safe yet! -->\n	\
	<xsl:variable name=\"link\">magnet:?xt=urn:sha1:<xsl:value-of select=\"current()\" />&amp;dn=<xsl:value-of select=\"translate(../../m:filename,' ','+')\"/></xsl:variable>\n	\
	<a href=\"{$link}\">Download using a Magnet link</a><br />\n	\
\n	\
	<xsl:variable name=\"linkb\">http://bitzi.com/lookup/<xsl:value-of select=\"current()\" /></xsl:variable>\n	\
	<a href=\"{$linkb}\">Online information by Bitzi.com (using SHA1)</a><br />\n	\
\n	\
<!--	\n	\
	<xsl:text>SHA1: </xsl:text>\n	\
	<xsl:value-of select=\"current()\" /><br />\n	\
-->\n	\
</xsl:template>\n	\
\n	\
\n	\
<xsl:template \n	\
	match=\"//m:digest[@dtype='ed2k']\"\n	\
	>\n	\
	<xsl:variable name=\"link\">ed2k://|file|<xsl:value-of select=\"../../m:filename\" /><xsl:text>|</xsl:text><xsl:value-of select=\"../../m:size\" /><xsl:text>|</xsl:text><xsl:value-of select=\"current()\" /><xsl:text>|/</xsl:text></xsl:variable>\n	\
	<a href=\"{$link}\">Download using eDonkey</a><br />\n	\
</xsl:template>\n	\
\n	\
<xsl:template match=\"/\">\n	\
	<html>\n	\
	<head>\n	\
		<meta http-equiv=\"content-type\" content=\"text/html; charset=UTF-8\" />\n	\
		<title>Metalinks</title>\n	\
	</head>\n	\
	<body>\n	\
	<h1>Metalinks</h1>\n	\
	<p class=\"center\">\n	\
	This is a collection of links that <em>might</em> work.<br /> These links are supplied with ABSOLUTELY NO WARRANTY in the hope they are usefull.\n	\
	</p>\n	\
	<hr />\n	\
	<table class=\"linktable\">\n	\
	<tbody>\n	\
	<xsl:for-each select=\"/m:metalinks/m:metalink\">\n	\
	<tr>\n	\
		<xsl:variable name=\"filename\"><xsl:value-of select=\"./m:filename\" /></xsl:variable>\n	\
		<td>\n	\
		<b>\n	\
		<a name=\"{$filename}\"></a>\n	\
		<xsl:value-of select=\"./m:filename\" /></b>\n	\
		<div class=\"fileinfo\">\n	\
		Size: <xsl:value-of select=\"./m:size\" /> bytes.<br />\n	\
			<xsl:apply-templates select=\"./m:digests/m:digest\" />\n	\
		</div>\n	\
		</td>\n	\
	</tr>\n	\
	</xsl:for-each>\n	\
	</tbody>\n	\
	</table>\n	\
	</body>\n	\
	</html>\n	\
</xsl:template>\n	\
\n	\
<!-- Hide unknown digests -->\n	\
<xsl:template priority=\"0\" match=\"//m:digest\" />\n	\
\n	\
</xsl:stylesheet>\n	\
");
