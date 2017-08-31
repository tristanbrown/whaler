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
            self.dir = guide.dir_repl
            self.file = guide.file_repl
            self.txt = guide.txt_repl
        except:
            self.dir = None
            self.file = None
            self.txt = None
        
    def run(self):
        """Runs the file generation script.
        """
        if self.multi != None:
            print("Running multi-replacement script.")
        elif self.dir != None:
            print("Running individual replacements.")
            self.ind_repl(self.dirs, self.dir, self.file, self.txt)
        else:
            print("Guide file is broken. Please check.")
    
    def ind_repl(self, dirs, dir, file, txt):
        """Performs all of the replacements given in the guide file.
        """
        folders = self.give_dirs(dirs)
        print(folders)
        return []
    
    def give_dirs(self, dirdefs):
        """Takes a list of directory identifiers and returns the list of 
        directories in the current location matching those conditions. 
        """
        dirlist = next(os.walk('.'))[1]
        for dir in dirlist:
            print(dir)
            print(self.stringcheck(dirdefs[0], dir))
    
    def stringcheck(self, rule, string):
        """Takes a string rule and determines if the string matches that rule.
        """
        if not "*" in rule:
            return rule in string
        elif rule[0] == "*":
            return string.endswith(rule[1:])
        elif rule[-1] == "*":
            return string.startswith(rule[:-1])
        else:
            start, end = rule.split("*")
            return string.startswith(start) and string.endswith(end)