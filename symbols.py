from cast.analysers import CustomObject, Bookmark

####################################################################################################

class Symbol:
    
    def __init__(self, name, parent=None):
        
        self.name = name
        self.parent = parent
        self.position = None
        self.kb_symbol= None

    def save(self, file):
        """
        Save the symbol
        """
        self.kb_symbol = CustomObject()
        self.kb_symbol.set_name(self.name)
        self.kb_symbol.set_type(self.type)
 
        self.kb_symbol.set_parent(self.parent.kb_symbol if self.parent else file)
        self.kb_symbol.save()
        
        self.kb_symbol.save_position(Bookmark(file, *self.position))

####################################################################################################
class Report(Symbol):
    
    def __init__(self, name):
        Symbol.__init__(self, name)
        self.list_querystrings = []
        self.log = None
    
    type = 'JasperReportReport'
    
    def save(self, file):
        """
        Save the symbol
        """
        Symbol.save(self, file)
        
        for querystring in self.list_querystrings:
            querystring.save(file)

####################################################################################################
class QueryString(Symbol):
    
    def __init__(self, name, sqlquery):
        Symbol.__init__(self, name)
        self.sqlquery = sqlquery

    type = 'JasperReportQueryString'
    
    def save(self, file):
        """
        Save the symbol
        """
        Symbol.save(self, file)
        self.kb_symbol.save_property('CAST_SQL_MetricableQuery.sqlQuery', self.sqlquery)
        #self.log.debug("self.parent.kb_symbol=" + self.parent.kb_symbol.name)