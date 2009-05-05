<!ELEMENT metalink (publisher?|license?|identity?|version?|copyright?|description?|tags?|files)+>
<!ATTLIST metalink version CDATA #IMPLIED>
<!ATTLIST metalink generator CDATA #IMPLIED>
<!ATTLIST metalink xmlns CDATA #IMPLIED>
<!ATTLIST metalink origin CDATA #IMPLIED>
<!ATTLIST metalink pubdate CDATA #IMPLIED>
<!ATTLIST metalink refreshdate CDATA #IMPLIED>
<!ATTLIST metalink type CDATA #IMPLIED>

<!ELEMENT identity (#PCDATA)>
<!ELEMENT version (#PCDATA)>
<!ELEMENT description (#PCDATA)>
<!ELEMENT copyright (#PCDATA)>
<!ELEMENT tags (#PCDATA)>
<!ELEMENT releasedate (#PCDATA)>

<!ELEMENT files (file+)>
<!ELEMENT file (changelog?|copyright?|description?|identity?|license?|logo?|mimetype?|multimedia?|publisher?|relations?|releasedate?|screenshot?|tags?|upgrade?|size?|language?|os?|verification?|resources)+>
<!ATTLIST file name CDATA #REQUIRED>

<!ELEMENT changelog (#PCDATA)>
<!ELEMENT logo (#PCDATA)>
<!ELEMENT mimetype (#PCDATA)>
<!ELEMENT relations (#PCDATA)>
<!ELEMENT screenshot (#PCDATA)>
<!ELEMENT upgrade (#PCDATA)>
<!ELEMENT size (#PCDATA)>
<!ELEMENT language (#PCDATA)>
<!ELEMENT os (#PCDATA)>
<!ELEMENT verification (hash*,signature?,pieces?)>
<!ELEMENT signature (#PCDATA)>
<!ATTLIST signature type CDATA #IMPLIED>
<!ATTLIST signature file CDATA #IMPLIED>

<!ELEMENT pieces (hash+)>
<!ATTLIST pieces type CDATA #REQUIRED>
<!ATTLIST pieces length CDATA #REQUIRED>

<!ELEMENT multimedia (video|audio)*>

<!ELEMENT resources (url+)>

<!ELEMENT url (#PCDATA)>
<!ATTLIST url type CDATA #IMPLIED>
<!ATTLIST url location CDATA #IMPLIED>
<!ATTLIST url preference CDATA #IMPLIED>
<!ATTLIST url maxconnections CDATA #IMPLIED>

<!ELEMENT license (name|url)+>
<!ELEMENT publisher (name|url)+>
<!ELEMENT name (#PCDATA)>

<!ELEMENT audio (bitrate?|codec?|duration?|resolution?|artist?|album?)>
<!ELEMENT video (bitrate?|codec?|duration?|resolution?|artist?|album?)>

<!ELEMENT hash (#PCDATA)>
<!ATTLIST hash piece CDATA #IMPLIED>
<!ATTLIST hash length CDATA #IMPLIED>
<!ATTLIST hash type CDATA #IMPLIED>


