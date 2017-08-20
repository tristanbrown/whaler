"""
 
"""

import os

class Analysis():
    """
    """
    def __init__(self):
        pass
        
    def groundstates_all(self):
        loc = os.getcwd()
        print(loc)
        structs = [x[0] for x in os.walk(loc)]
        print(structs)
        structs2 = next(os.walk('.'))[1]
        print(structs2)
        
    def groundstate(self, structure):
        pass