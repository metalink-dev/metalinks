#!/usr/bin/env python
########################################################################
#
# Project: Metalink Checker
# URL: http://www.nabber.org/projects/
# E-mail: webmaster@nabber.org
#
# Copyright: (C) 2007-2008, Neil McNab
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
# Filename: $URL$
# Last Updated: $Date$
# Author(s): Neil McNab
#
# Description:
#   Functions for accessing XML formatted data.
#
########################################################################

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
