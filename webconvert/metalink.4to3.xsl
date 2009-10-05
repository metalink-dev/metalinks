<?xml version="1.0" encoding="UTF-8"?>
<!-- Author: neil@nabber.org -->

<xsl:stylesheet xmlns="http://www.metalinker.org/"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:metalink4="urn:ietf:params:xml:ns:metalink"
		version="1.0">

  <xsl:output method="xml" encoding="utf-8" indent="yes" />

  <xsl:template match="/metalink4:metalink">

<metalink>

<xsl:if test="metalink4:origin">
<xsl:attribute name="origin">
<xsl:value-of select="metalink4:origin"/>
</xsl:attribute>
</xsl:if>

<xsl:if test="metalink4:dynamic">
<xsl:attribute name="type">dynamic</xsl:attribute>
</xsl:if>

<xsl:if test="metalink4:generator">
<xsl:attribute name="generator"><xsl:value-of select="metalink4:generator"/></xsl:attribute>
</xsl:if>

<files>
<!-- List file details -->
<xsl:for-each select="metalink4:file">

  <file>
<xsl:attribute name="name">
<xsl:value-of select="@name"/>
</xsl:attribute>

<xsl:if test="metalink4:size">
<size><xsl:value-of select="metalink4:size"/></size>
</xsl:if>

<xsl:if test="metalink4:os">
<os><xsl:value-of select="metalink4:os"/></os>
</xsl:if>

<xsl:if test="metalink4:version">
<version><xsl:value-of select="metalink4:version"/></version>
</xsl:if>

<!-- Verification -->
<verification>

<xsl:for-each select="metalink4:pieces">
<pieces>
<xsl:attribute name="type">
<xsl:value-of select="translate(@type,'-','')"/>
</xsl:attribute>
<xsl:attribute name="length">
<xsl:value-of select="@length"/>
</xsl:attribute>

<xsl:for-each select="metalink4:hash">
<hash>

<xsl:attribute name="piece">
<xsl:value-of select="position()-1" />
</xsl:attribute>

<xsl:value-of select="."/>
</hash>
</xsl:for-each>
</pieces>
</xsl:for-each>


<xsl:if test="metalink4:hash">

<xsl:for-each select="metalink4:hash">
    <hash>

<xsl:if test="@type">
<xsl:attribute name="type">
<xsl:value-of select="translate(@type,'-','')"/>
<!--
<xsl:value-of select="@type"/>
-->
</xsl:attribute>
</xsl:if>

<xsl:value-of select="."/>
</hash>
</xsl:for-each>
</xsl:if>

<!-- signature block -->
<xsl:if test="metalink4:signature">

<xsl:for-each select="metalink4:signature">
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

</verification>
<!--- URLs -->
  <resources>
<xsl:for-each select="metalink4:url">

    <url>

<xsl:if test="@type">
<xsl:attribute name="type">
<xsl:value-of select="@type"/>
</xsl:attribute>
</xsl:if>

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

<xsl:for-each select="metalink4:metaurl">

    <url>

<xsl:if test="@type">
<xsl:attribute name="type">
<xsl:value-of select="@type"/>
</xsl:attribute>
</xsl:if>

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

  </resources>
  </file>
</xsl:for-each>

</files>


</metalink>
  </xsl:template>
  
</xsl:stylesheet>
