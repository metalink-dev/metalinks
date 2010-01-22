<?xml version="1.0" encoding="UTF-8"?>
<!-- Author: neil@nabber.org 
Updated to match draft 26
-->

<xsl:stylesheet xmlns="urn:ietf:params:xml:ns:metalink"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:metalink="http://www.metalinker.org/"
		version="1.0">

  <xsl:output method="xml" encoding="utf-8" indent="yes" />

  <xsl:template match="/metalink:metalink">

<metalink>

<xsl:if test="@origin">
<origin>
<xsl:if test="@type='dynamic'">
<xsl:attribute name="dynamic">true</xsl:attribute>
</xsl:if>
<xsl:if test="@type='static'">
<xsl:attribute name="dynamic">false</xsl:attribute>
</xsl:if>

<xsl:value-of select="@origin"/>
</origin>
</xsl:if>

<xsl:if test="@generator">
<generator><xsl:value-of select="@generator"/></generator>
</xsl:if>

<!-- List file details -->
<xsl:for-each select="metalink:files/metalink:file">

  <file>
<xsl:attribute name="name">
<xsl:value-of select="@name"/>
</xsl:attribute>

<xsl:if test="metalink:size">
<size><xsl:value-of select="metalink:size"/></size>
</xsl:if>

<xsl:if test="metalink:os">
<os><xsl:value-of select="metalink:os"/></os>
</xsl:if>

<xsl:if test="metalink:version">
<version><xsl:value-of select="metalink:version"/></version>
</xsl:if>

<!-- Verification -->

<xsl:for-each select="metalink:verification/metalink:pieces">
<pieces>
<xsl:attribute name="type">
<xsl:value-of select="@type"/>
</xsl:attribute>
<xsl:attribute name="length">
<xsl:value-of select="@length"/>
</xsl:attribute>

<xsl:for-each select="metalink:hash">
<hash>
<xsl:value-of select="."/>
</hash>
</xsl:for-each>
</pieces>
</xsl:for-each>


<xsl:if test="metalink:verification/metalink:hash">

<xsl:for-each select="metalink:verification/metalink:hash">
    <hash>

<xsl:if test="@type">
<xsl:choose>
<xsl:when test="starts-with(@type, 'sha')">

<xsl:attribute name="type">sha-<xsl:value-of select="substring-after(@type,'sha')"/></xsl:attribute>

</xsl:when>
<xsl:otherwise>

<xsl:attribute name="type">
<xsl:value-of select="@type"/>
</xsl:attribute>

</xsl:otherwise>
</xsl:choose>
</xsl:if>


<xsl:value-of select="."/>
</hash>
</xsl:for-each>
</xsl:if>


<!-- signature block -->
<xsl:if test="metalink:verification/metalink:signature">

<xsl:for-each select="metalink:verification/metalink:signature">
<signature>

<xsl:if test="@type">
<xsl:attribute name="type">
<xsl:value-of select="@type"/>
</xsl:attribute>
</xsl:if>

<xsl:value-of select="."/>

</signature>

</xsl:for-each>
</xsl:if>

<!--- URLs -->
<xsl:for-each select="metalink:resources/metalink:url[not(@type='bittorrent')]">

<url>

<xsl:if test="@preference">
<xsl:attribute name="priority">
<xsl:value-of select="101-@preference"/>
</xsl:attribute>
</xsl:if>

<xsl:if test="@location">
<xsl:attribute name="location">
<xsl:value-of select="@location"/>
</xsl:attribute>
</xsl:if>

<xsl:value-of select="."/>

</url>

</xsl:for-each>

<xsl:for-each select="metalink:resources/metalink:url[@type='bittorrent']">

<metaurl>

<xsl:attribute name="type">torrent</xsl:attribute>

<xsl:if test="@preference">
<xsl:attribute name="priority">
<xsl:value-of select="101-@preference"/>
</xsl:attribute>
</xsl:if>

<xsl:if test="@location">
<xsl:attribute name="location">
<xsl:value-of select="@location"/>
</xsl:attribute>
</xsl:if>

<xsl:value-of select="."/>

</metaurl>

</xsl:for-each>


  </file>
</xsl:for-each>


</metalink>
  </xsl:template>
  
</xsl:stylesheet>
