import re
from cast.analysers import log
from symbols import Report, QueryString
import os
from cast.application import open_source_file

# some funky code from https://stackoverflow.com/questions/6949395/is-there-a-way-to-get-a-line-number-from-an-elementtree-element
import sys
sys.modules['_elementtree'] = None
try:
    sys.modules.pop('xml.etree.ElementTree')
except KeyError:
    pass
import xml.etree.ElementTree as ET


def parse(text, path=None, log=None):
    """
    Parse a bpel file
    :param text: str
    
    :return: symbols.Process
    """
    root = get_root(text)
    return parse_report(root, path, log)


def parse_report(node, path=None, log=None):
    list_report = []
    if get_tag_name(node) == 'jasperReport':
        node_report = node
        obj_report = Report(node_report.attrib['name'])
        obj_report.position = get_position(node_report)
        index = 0
        for node_sql in find_all_querystring(node):
            index += 1
            #log.info("node sql " + str(index))
            obj_qs = parse_querystring(node_sql, obj_report, index, log)
            obj_qs.log= log
            obj_report.list_querystrings.append(obj_qs)
        
        list_report.append(obj_report)
    return list_report

def parse_querystring(node_qs, obj_report, index, log=None):
    querystring = node_qs.text.replace('<![CDATA[\n','').replace(']]>','').replace('\n',' ')
    querystring = re.sub('[\t ]+',' ', querystring)
    log.debug("querystring="+querystring)
    obj_qs = QueryString("queryString"+str(index), querystring)
    obj_qs.parent = obj_report
    obj_qs.sqlquery = querystring
    obj_qs.position = get_position(node_qs)
    return obj_qs

def find_nodes(node, name):
    """
    find all items of given 'name' recursively
    """
    result = []

    if get_tag_name(node) == name:
        result.append(node)

    for child in node:
        result.extend(find_nodes(child, name))

    return result


def find_all_querystring(node):
    return find_nodes(node, 'queryString')


def get_root(text):

    class LineNumberingParser(ET.XMLParser):
        def _start(self, *args, **kwargs):
            # Here we assume the default XML parser which is expat
            # and copy its element position attributes into output Elements
            element = super(self.__class__, self)._start(*args, **kwargs)
            element.start_line_number = self.parser.CurrentLineNumber
            element.start_column_number = self.parser.CurrentColumnNumber
            element._start_byte_index = self.parser.CurrentByteIndex
            return element
    
        def _end(self, *args, **kwargs):
            element = super(self.__class__, self)._end(*args, **kwargs)
            element.end_line_number = self.parser.CurrentLineNumber
            element.end_column_number = self.parser.CurrentColumnNumber
            element._end_byte_index = self.parser.CurrentByteIndex
            return element    
    
    return ET.fromstring(text, LineNumberingParser())
        



def get_tag_name(element):
    """
    remove the {...}tag and return tag
    """
    if '}' in element.tag:
        return element.tag.split('}')[1]
    return element.tag


def get_position(node):
    return (node.start_line_number, node.start_column_number, node.end_line_number, node.end_column_number)


    

