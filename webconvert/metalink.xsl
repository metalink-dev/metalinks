<?xml version="1.0" encoding="UTF-8"?>
<!-- Author: webmaster@nabber.org -->

<xsl:stylesheet xmlns="http://www.w3.org/1999/xhtml"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:metalink="http://www.metalinker.org/"
                xmlns:metalink4="urn:ietf:params:xml:ns:metalink"
		version="1.0">

  <xsl:output method="xml" encoding="utf-8"
	doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"
	doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"/>

  <xsl:template match="/metalink4:metalink">
    <html>
      <head>
        <title>
          Metalink v4
        </title>

      </head>
      <body>
        <a href="http://www.metalinker.org"><img src="metalink_logo_small.png" border="0" /></a>

        <p>
                Metalink is an Open Standard that bundles the various ways (<abbr title="File Transfer Protocol">FTP</abbr>/<abbr
title="Web">HTTP</abbr>/<abbr title="Peer-to-Peer">P2P</abbr>) to get files into one format for easier downloads. That's probably already <a
class="nounderline" style="color: black; font-weight: bold" href="http://en.wikipedia.org/wiki/Metalink" target="_blank">more detail</a> than you want.
It's just...Simpler. Faster. More Reliable. Better.

                <br/><br/>
For more info, <a class="nounderline" style="color: black; font-weight: bold" href="http://www.metalinker.org/why.html">read on</a>...or, just <a
class="nounderline"
style="color: black; font-weight: bold" href="http://www.metalinker.org/samples.html">get a supported download program &amp; try it</a>!
                </p>

        <h2><xsl:value-of select="metalink4:identity"/><xsl:text> </xsl:text><xsl:value-of select='metalink4:version'/></h2>

<!-- List file summary -->

<h3>Table of Contents</h3>
        <table border="1">
            <tr>
                <th>Identity</th>
                <th>File Name</th>
                <th>Size (Bytes)</th>
                <th>OS</th>
            </tr>

        <xsl:for-each select="metalink4:file">
        <tr>
                <td>
                        <a><xsl:attribute name="href">#<xsl:value-of select="@name"/></xsl:attribute><xsl:value-of select="metalink4:identity"/></a>
                </td>
                <td>
                        <a><xsl:attribute name="href">#<xsl:value-of select="@name"/></xsl:attribute><xsl:value-of select="@name"/></a>
                </td>
                <td>
                        <xsl:value-of select="format-number(metalink4:size, '###,###,###,###,###')"/>
                </td>
                <td>
                        <xsl:value-of select="metalink4:os"/>
                </td>
        </tr>
        </xsl:for-each>
</table>

<!-- List file details -->

<xsl:for-each select="metalink4:file">
<h3><a><xsl:attribute name="name"><xsl:value-of select="@name"/></xsl:attribute><xsl:value-of select="metalink4:identity"/> (<xsl:value-of select="@name"/>)</a></h3>

<p>
<xsl:if test="metalink4:publisher/@name">
Publisher:
<xsl:choose>
<xsl:when test="metalink4:publisher/@url">
        <a><xsl:attribute name="href"><xsl:value-of select="metalink4:publisher/@url"/></xsl:attribute><xsl:value-of select="metalink4:publisher/@name"/></a>
</xsl:when>
<xsl:otherwise>
        <xsl:value-of select="metalink4:publisher/@name"/>
</xsl:otherwise>
</xsl:choose>
<br />
</xsl:if>

<xsl:if test="metalink4:license/@name">
License:
<xsl:choose>
<xsl:when test="metalink4:license/@url">
        <a><xsl:attribute name="href"><xsl:value-of select="metalink4:license/@url"/></xsl:attribute><xsl:value-of select="metalink4:license/@name"/></a>
</xsl:when>
<xsl:otherwise>
        <xsl:value-of select="metalink4:license/@name"/>
</xsl:otherwise>
</xsl:choose>
<br />
</xsl:if>

</p>

<!-- metalink description -->

<xsl:if test="metalink4:description">
        <h3>Description</h3>
        <p><xsl:value-of select='metalink4:description'/></p>
</xsl:if>

<!-- Verification Table -->
<xsl:if test="metalink4:hash">
        <table border="1">
            <tr>
                <th>Hash Type</th>
                <th>Hash Value</th>
            </tr>
<xsl:for-each select="metalink4:hash">
                <xsl:sort select="@type"
                          data-type="text"
                          order="ascending"/>
<tr>
        <td style="text-transform: uppercase">
                <xsl:value-of select="@type"/>
        </td>
        <td>
                <xsl:value-of select="."/>
        </td>
</tr>
</xsl:for-each>
</table>
</xsl:if>


<!-- Signature Table -->
<xsl:if test="metalink4:signature">
        <table border="1">
            <tr>
                <th>Signature Type</th>
                <th>Signature Value</th>
            </tr>
<xsl:for-each select="metalink4:signature">
<tr>
        <td style="text-transform: uppercase">
                <xsl:value-of select="@type"/>
        </td>
        <td>
                <pre><xsl:value-of select="."/></pre>
        </td>
</tr>
</xsl:for-each>
</table>
</xsl:if>

<!--- URL table -->
        <table border="1">
            <tr>
                <th>Priority</th>
                <th>Location</th>
                <th>Type</th>
                <th>URL</th>
            </tr>
<xsl:for-each select="metalink4:url">
                <xsl:sort select="@preference"
                          data-type="number"
                          order="descending"/>
                <tr>
                    <td>
                        <xsl:value-of select="@priority"/>
                    </td>
                    <td style="text-transform: uppercase">
                        <xsl:value-of select="@location"/>
                    </td>
                    <td style="text-transform: uppercase">
                        <xsl:value-of select="@type"/>
                    </td>
                    <td>
                        <a><xsl:attribute name="href"><xsl:value-of select="."/></xsl:attribute><xsl:value-of select="."/></a>
                    </td>
                </tr>
</xsl:for-each>
<xsl:for-each select="metalink4:metaurl">
                <xsl:sort select="@preference"
                          data-type="number"
                          order="descending"/>
                <tr>
                    <td>
                        <xsl:value-of select="@priority"/>
                    </td>
                    <td style="text-transform: uppercase">
                        <xsl:value-of select="@location"/>
                    </td>
                    <td style="text-transform: uppercase">
                        <xsl:value-of select="@type"/>
                    </td>
                    <td>
                        <a><xsl:attribute name="href"><xsl:value-of select="."/></xsl:attribute><xsl:value-of select="."/></a>
                    </td>
                </tr>
</xsl:for-each>
</table>
</xsl:for-each>

    </body>
    </html>
  </xsl:template>

  <xsl:template match="/metalink:metalink">
    <html>
      <head>
        <title>
          Metalink v3 - <xsl:value-of select="metalink:identity"/>
        </title>
      </head>
      <body>
	<a href="http://www.metalinker.org"><img src="metalink_logo_small.png" border="0" /></a>

	<p>
		Metalink is an Open Standard that bundles the various ways (<abbr title="File Transfer Protocol">FTP</abbr>/<abbr 
title="Web">HTTP</abbr>/<abbr title="Peer-to-Peer">P2P</abbr>) to get files into one format for easier downloads. That's probably already <a 
class="nounderline" style="color: black; font-weight: bold" href="http://en.wikipedia.org/wiki/Metalink" target="_blank">more detail</a> than you want. 
It's just...Simpler. Faster. More Reliable. Better.

		<br/><br/>
For more info, <a class="nounderline" style="color: black; font-weight: bold" href="http://www.metalinker.org/why.html">read on</a>...or, just <a 
class="nounderline" 
style="color: black; font-weight: bold" href="http://www.metalinker.org/samples.html">get a supported download program &amp; try it</a>!
		</p>

        <h2><xsl:value-of select="metalink:identity"/><xsl:text> </xsl:text><xsl:value-of select='metalink:version'/></h2>

<p>

<xsl:if test="metalink:publisher/metalink:name">
Publisher: 
<xsl:choose>
<xsl:when test="metalink:publisher/metalink:url">
	<a><xsl:attribute name="href"><xsl:value-of select="metalink:publisher/metalink:url"/></xsl:attribute><xsl:value-of select="metalink:publisher/metalink:name"/></a>
</xsl:when>
<xsl:otherwise>
	<xsl:value-of select="metalink:publisher/metalink:name"/>
</xsl:otherwise>
</xsl:choose>
<br />
</xsl:if>

<xsl:if test="metalink:license/metalink:name">
License: 
<xsl:choose>
<xsl:when test="metalink:license/metalink:url">
	<a><xsl:attribute name="href"><xsl:value-of select="metalink:license/metalink:url"/></xsl:attribute><xsl:value-of select="metalink:license/metalink:name"/></a>
</xsl:when>
<xsl:otherwise>
	<xsl:value-of select="metalink:license/metalink:name"/>
</xsl:otherwise>
</xsl:choose>
<br />
</xsl:if>

<xsl:if test="metalink:tags">
Keywords: <xsl:value-of select="metalink:tags"/>
</xsl:if>
</p>


<!-- metalink description -->

<xsl:if test="metalink:description">
	<h3>Description</h3>
	<p><xsl:value-of select='metalink:description'/></p>
</xsl:if>



<!-- List file summary -->

<h3>Table of Contents</h3>
        <table border="1">
            <tr>
                <th>File Name</th>
                <th>Size (Bytes)</th>
                <th>OS</th>
            </tr>

	<xsl:for-each select="metalink:files/metalink:file">
	<tr>
		<td>
			<a><xsl:attribute name="href">#<xsl:value-of select="@name"/></xsl:attribute><xsl:value-of select="@name"/></a>
		</td>
		<td>
			<xsl:value-of select="format-number(metalink:size, '###,###,###,###,###')"/>
		</td>
		<td>
			<xsl:value-of select="metalink:os"/>
		</td>
	</tr>
	</xsl:for-each>
</table>

<!-- List file details -->

<xsl:for-each select="metalink:files/metalink:file">
<h3><a><xsl:attribute name="name"><xsl:value-of select="@name"/></xsl:attribute><xsl:value-of select="@name"/></a></h3>

<!-- Verification Table -->
<xsl:if test="metalink:verification/metalink:hash">
        <table border="1">
            <tr>
                <th>Hash Type</th>
                <th>Hash Value</th>
            </tr>
<xsl:for-each select="metalink:verification/metalink:hash">
                <xsl:sort select="@type"
                          data-type="text"
                          order="ascending"/>
<tr>
	<td style="text-transform: uppercase">
		<xsl:value-of select="@type"/>
	</td>
	<td>
		<xsl:value-of select="."/>
	</td>
</tr>
</xsl:for-each>
</table>
</xsl:if>


<!-- Signature Table -->
<xsl:if test="metalink:verification/metalink:signature">
        <table border="1">
            <tr>
                <th>Signature Type</th>
                <th>Signature Value</th>
            </tr>
<xsl:for-each select="metalink:verification/metalink:signature">
<tr>
	<td style="text-transform: uppercase">
		<xsl:value-of select="@type"/>
	</td>
	<td>
		<pre><xsl:value-of select="."/></pre>
	</td>
</tr>
</xsl:for-each>
</table>
</xsl:if>


<!--- URL table -->
        <table border="1">
            <tr>
                <th>Preference</th>
                <th>Location</th>
                <th>Type</th>
                <th>URL</th>
            </tr>
<xsl:for-each select="metalink:resources/metalink:url">
                <xsl:sort select="@preference"
                          data-type="number"
                          order="descending"/>
                <tr>
                    <td>
                        <xsl:value-of select="@preference"/>
                    </td>
                    <td style="text-transform: uppercase">
                        <xsl:value-of select="@location"/>
                    </td>
                    <td style="text-transform: uppercase">
                        <xsl:value-of select="@type"/>
                    </td>
                    <td>
                        <a><xsl:attribute name="href"><xsl:value-of select="."/></xsl:attribute><xsl:value-of select="."/></a>
                    </td>
                </tr>
</xsl:for-each>
</table>


</xsl:for-each>


      </body>
    </html>
  </xsl:template>
  
</xsl:stylesheet>
