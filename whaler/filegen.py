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
        self.dirs = self.give_dirs(guide.dirs)
        print(self.dirs)
        try:
            self.multi = guide.multi_repl
        except:
            self.multi = None
            
        try:
            self.dirkey = guide.dir_repl
            self.filekey = guide.file_repl
            self.txtkey = guide.txt_repl
        except:
            self.dirkey = None
            self.filekey = None
            self.txtkey = None
        
    def run(self):
        """Runs the file generation script.
        """
        if self.multi != None:
            print("Running multi-replacement script.")
        elif self.dirkey != None:
            print("Running individual replacements.")
            self.ind_repl(self.dirkey, self.filekey, self.txtkey)
        else:
            print("Guide file is broken. Please check.")
    
    def ind_repl(self, dirkey, filekey, txtkey):
        """Performs all of the replacements given in the guide file.
        """
        for dir in self.dirs:
            for file in self.get_files(dir):
                self.repl_file(dir, file, dirkey, filekey, txtkey)
        
    def repl_file(self, dir, file, dirkey, filekey, txtkey):
        """Uses keys to replace strings at the directory, filename, and text 
        levels. 
        """
        startloc = os.path.join(self.loc, dir, file)
        newdir = self.dictreplace(dir, dirkey)
        newfile = self.dictreplace(file, filekey)
        enddir = os.path.join(self.loc, newdir)
        endloc = os.path.join(enddir, newfile)
        if not os.path.exists(enddir):
            os.makedirs(enddir)
        if startloc != endloc:
            print("Reading " + startloc)
            print("Writing " + endloc)
            self.replace_all_vals(startloc, endloc, txtkey)
    
    def give_dirs(self, dirdefs):
        """Takes a list of directory identifiers and returns the list of 
        directories in the current location matching those conditions. 
        """
        dirlist = next(os.walk('.'))[1]
        return [dir for dir in dirlist
                if self.check_all_rules(dirdefs, dir)]
                
    def get_files(self, dir):
        """Gives a list of the files in a given directory."""
        path = os.path.join(self.loc, dir)
        return [f for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f))]
    
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
    
    def check_all_rules(self, rulelist, string):
        """Does stringcheck for all the given rules, and determines if any of
        them applies. 
        """
        checks = []
        for rule in rulelist:
            checks.append(self.stringcheck(rule, string))
        
        return True in checks
    
    def dictreplace(self, string, keydict):
        """Uses a dictionary as a key for string replacements. 
        """
        for old, new in keydict.items():
            string = string.replace(old, new)
        return string
    
    def replace_all_vals(self, infile, outfile, keydict):
        """Replaces all instances of a particular string in a file, using a
        dictionary of old:new text replacements as the key.
        """
        with open(infile, "rt") as fin:
            with open(outfile, "wt") as fout:
                for line in fin:
                    fout.write(self.dictreplace(line, keydict))