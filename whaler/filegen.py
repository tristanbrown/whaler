"""
This module contains the functions necessary to systematically modify files and
directories. 
"""

import os
import sys

class Generator():
    """An object that can generate new files based on a set of template files
    and a guide containing the desired replacements. 
    """
    def __init__(self, guidefile):
        # Set the path variables and get the guide file.
        self.loc = os.getcwd()
        sys.path.append(self.loc)
        guide = __import__(guidefile)
        
        # Set the variables given by the guide. 
        self.dirs = guide.dirs
        try:
            self.multi = guide.multi_repl
        except:
            self.multi = None
            
        try:
            self.dir_r = guide.dir_repl
            self.file_r = guide.file_repl
            self.txt_r = guide.txt_repl
        except:
            self.dir_r = None
            self.file_r = None
            self.txt_r = None
        
    def run(self):
        """Runs the file generation script.
        """
        if self.multi != None:
            print("Running multi-replacement script.")
        elif self.dir_r != None:
            print("Running individual replacements.")
        else:
            print("Guide file is broken. Please check.")
    