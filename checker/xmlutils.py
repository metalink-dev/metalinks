import xml.dom.minidom

def get_child_nodes(rootnode, subtag):
    '''
    Extract specific child tag names.
    First parameter, XML node
    Second parameter, name (string) of child node(s) to look for
    Returns a list of child nodes
    '''
    children = []
    for childnode in rootnode.childNodes:
        if childnode.nodeName == subtag:
            children.append(childnode)
            
    return children

def get_subnodes(rootnode, subtags):
    '''
    First parameter, XML node
    Second parameter, tree in array form for names (string) of child node(s) to look for
    Returns a list of child nodes (searched recursively)
    '''
    children = []
    child_nodes = get_child_nodes(rootnode, subtags[0])
    if (len(subtags) == 1):
        return child_nodes
    
    for child in child_nodes:
        child_nodes = get_subnodes(child, subtags[1:])
        children.extend(child_nodes)
        
    return children

def get_texttag_values(xmlfile, tag):
    '''
    Get values for selected tags in an XML file
    First parameter, XML file to parse
    Second parameter, tag to search for in XML file
    Returns a list of text values found
    '''
    looking_for = []
    try:
        datasource = open(xmlfile)
    except IOError:
        return looking_for

    dom2 = xml.dom.minidom.parse(datasource)   # parse an open file
    datasource.close()
    return get_xml_tag_strings(dom2, tag)

def get_tags(xmlfile, tag):
    looking_for = []
    try:
        datasource = open(xmlfile)
    except IOError:
        return looking_for

    dom2 = xml.dom.minidom.parse(datasource)   # parse an open file
    datasource.close()
    return get_subnodes(dom2, tag)

def get_xml_tag_strings(item, tag):
    '''
    Converts an XML node to a list of text for specified tag
    First parameter, XML node object
    Second parameter, tag tree names to search for
    Returns a list of text value for this tag
    '''   
    return get_xml_item_strings(get_subnodes(item, tag))

def get_xml_item_strings(items):
    '''
    Converts XML nodes to text
    First parameter, list of XML Node objects
    Returns, list of strings as extracted from text nodes in items
    '''
    stringlist = []
    for myitem in items:
        stringlist.append(myitem.firstChild.nodeValue.strip())
    return stringlist

def get_attr_from_item(item, name):
    '''
    Extract the attribute from the XML node
    First parameter, item XML node
    Returns value of the attribute
    '''
    local_file = ""

    for i in range(item.attributes.length):
        if item.attributes.item(i).name == name:
            local_file = item.attributes.item(i).value
            
    return local_file

###################################################

