<?php

function metalink3to4($xmltext) {
    return xmlconvert($xmltext, 'metalink.3to4.xsl');
}

function metalink4to3($xmltext) {
    return xmlconvert($xmltext, 'metalink.4to3.xsl');
}


function xmlconvert($sXml, $xslsheet){
# LOAD XML FILE
$XML = new DOMDocument();
$XML->loadXML( $sXml );

# START XSLT
$xslt = new XSLTProcessor();
$XSL = new DOMDocument();
$XSL->load($xslsheet, LIBXML_NOCDATA);
$xslt->importStylesheet( $XSL );
return $xslt->transformToXML( $XML ); 
}
?>
