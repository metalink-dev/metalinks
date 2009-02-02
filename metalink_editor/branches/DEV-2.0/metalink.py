import xml.sax
import xml.sax.handler
import xml.sax.saxutils
from xml.sax.xmlreader import AttributesNSImpl
import StringIO

class Metalink(object):
    def __init__(self):
        self.files = []
    
    def save(self, output):
        xml = MetalinkXml(output)
        xml.addElement("generator", "Metalink Editor", {"version": "2.0"})
        xml.startElement("files")
        for file in self.files:
            file.save(xml)
        xml.endElement("files")
        xml.close()
    
    def saveFile(self, filename):
        f = open(filename, "wb")
        self.save(f)
        f.close()
    
    def getXml(self):
        buf = StringIO.StringIO()
        self.save(buf)
        return buf.getvalue()

class MetalinkFile(object):
    def __init__(self, name=""):
        self.name = name
        self.size = 0
        self.identity = ""
        self.version = ""
        self.description = ""
        self.resources = []
        self.hashes = []
    
    # Getters and setters
    def getName(self):
        return self._name
    
    def setName(self, name):
        if not self.validateName(name): raise Exception("MetalinkFile: Invalid filename")
        self._name = name
    
    # Properties
    name = property(getName, setName)
    
    def validateName(self, name):
        if name.startswith("/") or name.startswith("./"): return False
        if name.startswith("../") or name.find("/../") != -1: return False
        if name.endswith("/.."): return False
        return True
    
    def save(self, xml):
        xml.startElement("file", {"name": self.name})
        xml.addElement("identity", self.identity)
        xml.addElement("version", self.version)
        xml.addElement("description", self.description)
        if self.size > 0: xml.addElement("size", str(self.size))
        if len(self.hashes) > 0:
            xml.startElement("verification")
            for hash in self.hashes:
                hash.save(xml)
            xml.endElement("verification")
        xml.startElement("resources")
        for res in self.resources:
            res.save(xml)
        xml.endElement("resources")
        xml.endElement("file")
    
class MetalinkResource(object):
    def __init__(self, type="url", uri=""):
        self.type = type
        self.uri = uri
    
    def save(self, xml):
        if self.type == "url":
            xml.addElement("url", self.uri)
        else:
            xml.addElement("metadata", self.uri, {"type":self.type})

class MetalinkHash(object):
    def __init__(self, type="", hash=""):
        self.type = type
        self.hash = hash
    
    def save(self, xml):
        xml.addElement("hash", self.hash, {"type":self.type})

# Metalink loading

class MetalinkParser(xml.sax.handler.ContentHandler):
    def parse(self, source):
        parser = xml.sax.make_parser()
        parser.setFeature(xml.sax.handler.feature_namespaces, 1)
        parser.setContentHandler(self)
        parser.parse(source)
    
    def startDocument(self):
        self.metalink = Metalink()
        self.elements = []
        self.attrlist = []
        self.content = ""
    
    def startElementNS(self, (uri, localname), qname, attrs):
        if uri != "urn:ietf:params:xml:ns:metalink": return
        self.elements.append(localname)
        attrs = self.processAttrs(attrs)
        self.attrlist.append(attrs)
        self.content = ""
        # Process start tags (do as little as possible here)
        if self.elements == ['metalink', 'files', 'file']:
            self.file = MetalinkFile()
            if attrs.has_key('name'): self.file.name = attrs['name']
    
    def endElementNS(self, (uri, localname), qname):
        if uri != "urn:ietf:params:xml:ns:metalink": return
        attrs = self.attrlist.pop()
        content = self.content.strip()
        #print "end:", self.elements, attrs
        #print "content: '" + content + "'"
        # Process end tags. Here we know everything we need to know.
        if self.elements == ['metalink', 'files', 'file']:
            if self.file.name != "": self.metalink.files.append(self.file)
        elif self.elements == ['metalink', 'files', 'file', 'identity']:
            self.file.identity = content
        elif self.elements == ['metalink', 'files', 'file', 'version']:
            self.file.version = content
        elif self.elements == ['metalink', 'files', 'file', 'description']:
            self.file.description = content
        elif self.elements == ['metalink', 'files', 'file', 'size']:
            self.file.size = long(content)
        elif self.elements == ['metalink', 'files', 'file', 'verification', 'hash']:
            if attrs.has_key("type"):
                self.file.hashes.append(MetalinkHash(attrs["type"], content))
        elif self.elements == ['metalink', 'files', 'file', 'resources', 'url']:
            self.file.resources.append(MetalinkResource("url", content))
        elif self.elements == ['metalink', 'files', 'file', 'resources', 'metadata']:
            if attrs.has_key("type"):
                self.file.resources.append(MetalinkResource(attrs["type"], content))
        self.elements.pop()
        self.content = ""
    
    def characters(self, content):
        self.content += content
    
    def processAttrs(self, attrs):
        result = {}
        for ((namespace, localname), value) in attrs.items():
            result[localname] = value
        return result

def loadFile(source):
    mlparser = MetalinkParser()
    mlparser.parse(source)
    return mlparser.metalink

# Metalink saving

class MetalinkXml:
    def __init__(self, output, compact=False):
        self.ns = "urn:ietf:params:xml:ns:metalink"
        if not compact:
            self.indent = "  "
            self.newline = "\n"
        else:
            self.indent = ""
            self.newline = ""
        self.depth = 0
        self.xml = xml.sax.saxutils.XMLGenerator(output, "utf-8")
        self.xml.startDocument()
        self.xml.startPrefixMapping("", self.ns)
        self.startElement("metalink")
    
    def startElement(self, name, attrs={}, newline=True):
        self.addContent(self.indent*self.depth)
        self.depth += 1
        attrs = self.getAttrs(attrs)
        self.xml.startElementNS((self.ns, name), name, attrs)
        if newline: self.addContent(self.newline)
    
    def endElement(self, name, newline=True, newlineAfter=True):
        self.depth -= 1
        if newline: self.addContent(self.indent*self.depth)
        self.xml.endElementNS((self.ns, name), name)
        if newlineAfter: self.addContent(self.newline)
    
    def addContent(self, content):
        self.xml.characters(content)
    
    def addElement(self, name, content="", attrs={}, addEmpty=False, newlines=False):
        if content == "" and addEmpty == false: return
        self.startElement(name, attrs, newlines)
        if newlines: self.addContent(self.indent*self.depth)
        self.addContent(content)
        if newlines: self.addContent(self.newline)
        self.endElement(name, newlines)
    
    def getAttrs(self, attrs={}):
        attr_values = {}
        attr_qnames = {}
        for key, value in attrs.iteritems():
            attr_values[(None, key)] = value
            attr_qnames[(None, key)] = key
        return AttributesNSImpl(attr_values, attr_qnames)
    
    def close(self):
        self.endElement("metalink", newlineAfter=False)
        self.xml.endPrefixMapping("")
        self.xml.endDocument()

ml = loadFile("test.metalink")
print ml.getXml()
ml.saveFile("generated.xml")
