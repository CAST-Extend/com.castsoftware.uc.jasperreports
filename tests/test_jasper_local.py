import traceback
import unittest
import cast.analysers.test
from cast.analysers import filter

'''
Created on May 27, 2019

@author: MMR
'''


class Test(unittest.TestCase):
    
    def testRunAnalysisUA(self):
        print("start testRunAnalysisUA")

        # UA DevBooster
        analysis = cast.analysers.test.UATestAnalysis('JasperReport')
        analysis.add_database_table('Orders', 'SQL')
        analysis.add_selection('sample1')
        analysis.set_verbose(True)
        
        try:
            analysis.run()
        except:
            tb = traceback.format_exc()
            if "Duplicate guid found" in tb:
                print("warning:" + tb)
            raise RuntimeError(tb)

        print("Analysis statistics")
        analysis.print_statistics()
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    
    
