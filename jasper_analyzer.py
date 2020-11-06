from cast.analysers import ua, log, create_link, CustomObject, Bookmark
from cast.application import open_source_file #@UnresolvedImport
import re
import os
import lxml.etree as ET
from lxml.etree import ElementTree
import traceback
from jrxml_parser import parse, get_tag_name


class JasperReportAnalysisExtension(ua.Extension):

    
    #################################################################
    
    def __init__(self):
         
        # do we have the correct UA selected or not
        self.active = True
        # default extension list (for unit tests)
        # same as in metamodel...
        self.extensions = ['.jrxml']
     
        self.nb_jrxml_files = 0
                
        self.nb_reports = 0
        self.nb_sqlqueries = 0
        
    #################################################################
    
    def start_analysis(self):
        # resistant (for unit tests)
        try:
            options = cast.analysers.get_ua_options()               #@UndefinedVariable dynamically added
            if not 'JasperReport' in options:
                # language not selected : inactive
                self.active = False
            else:
                # options :
                self.extensions = options['JasperReport'].extensions
        except:
            pass
         
    #################################################################
    
    def start_file(self, file):             # Extension point : each file
        if not self.active:
            return # no need to do something
 
        filepath = file.get_path()
        _, ext = os.path.splitext(filepath)
 
        if not ext in self.extensions:
            return
        log.debug('\t JasperReportAnalysisExtension start_file %s: %s)' % (os.path.basename(filepath), filepath))
 
        try:
            with open_source_file(filepath) as f:
                self.nb_jrxml_files += 1
                list_reports = parse(f.read(), filepath, log)
                for report in list_reports: 
                    report.save(file)
                    self.nb_reports += 1
                    self.nb_sqlqueries += len(report.list_querystrings)

        except:
            log.warning('Issue analyzing file ' + traceback.format_exc())                

    """   
    def start_object(self, object):
        log.info('Start object %s' % str(object))
    """
    
    """
    def end_object(self, object):
        log.debug('   end_object %s ' % object.get_name()) 
        None
    """    
        
    ##########################################################################################################################
  
    def end_analysis(self):
        self.log_end_analysis()
  
    ##########################################################################################################################
        
    def log_end_analysis(self):
        log.info("=======================================================================================")
        log.info('JasperReportAnalysisExtension end_analysis UA')        
        log.info("=======================================================================================")
        log.info("Total Number of jrxml files parsed : %s" % str(self.nb_jrxml_files))
        log.info("Total Number of Reports : %s" % str(self.nb_reports))
        log.info("Total Number of SQL Queries : %s" % str(self.nb_sqlqueries))
        log.info("=======================================================================================")        
        
##########################################################################################################################        


def read_xml_file(path, log=None):
    """
    Read an xml file and return the root node as for lxml.etree
    """
    def remove_utf8_from_xml(fileContent):
        """
        Removes the header from the file content.
        
    <?xml version="1.0" encoding="UTF-8"?>
        """
        indexStart = fileContent.find('<?xml')
        if indexStart < 0:
            return fileContent
        
        indexStart = fileContent.find('<', indexStart + 2)
        if indexStart < 0:
            return fileContent
    
        return fileContent[indexStart:]
    
    def remove_xmlns_from_xml(fileContent):
        """
        Removes the "xmlns=" part from file content because lxml api supports this part only by specifying exactly
        its value whenever we want to access a part of xml content, and its value can change between xml files.
        
    <web-app xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://java.sun.com/xml/ns/javaee" xmlns:web="http://java.sun.com/xml/ns/javaee/web-app_2_5.xsd" xsi:schemaLocation="http://java.sun.com/xml/ns/javaee http://java.sun.com/xml/ns/javaee/web-app_2_5.xsd" id="WebApp_ID" version="2.5">
    </web-app>
        """
        if not 'xmlns=' in fileContent:
            return fileContent
        
        indexStart = fileContent.find('xmlns=')
        indexValueStart = fileContent.find('"', indexStart)
        if indexValueStart < 0:
            return fileContent
        indexValueEnd = fileContent.find('"', indexValueStart + 1)
        if indexValueEnd < 0:
            return fileContent
    
        return fileContent.replace(fileContent[indexStart:indexValueEnd + 1], '')
    
    '''
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
    '''
   
    with open_source_file(path) as f:
        file_content = f.read()
        file_content = remove_utf8_from_xml(file_content)
        file_content = remove_xmlns_from_xml(file_content)
        
        parser=ET.XMLParser(recover=True)
        return ET.fromstring(file_content, parser)
        #return get_root(file_content)