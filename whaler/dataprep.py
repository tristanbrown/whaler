"""
This module contains the functions necessary to extract data from text files
and put it into numpy arrays to be usable by other functions. 
"""

import os
import re
import numpy as np

class IO():
    """An object that points to a desired file location and either extracts data
    from an existing text file, or writes data to a text file. 
    """
    def __init__(self, filename='', dir=''):
        self.fn = os.path.join(dir, filename)

        if os.path.exists(self.fn):
            #print("%s found." % self.fn)
            pass
        else:
            print("%s does not yet exist." % self.fn)
    
    def get_values(self, structure, exten, filecheck, extractor):
        """For a given structure, identifies all of the relevant, current log
        files. Runs filecheck to verify convergence, and then uses the extractor
        to acquire the desired values from the file. The values arereturned as a state:value dictionary. 
        """
        path = self.fn
        
        # Narrows it down to the appropriate log files.
        logs = self.files_end_with(exten)
        
        # Unpacks filetypes.
        ftypes = {file:self.getcalctype(file) for file in logs}
        
        try:
            iter, state, type = (zip(*ftypes.values()))
            # Removes invalid and outdated files, marking the log. 
            curriter = max(iter)
            
            values = {
                v[1]:extractor(k, path) for (k,v) in ftypes.items() 
                if v[0] == curriter and filecheck(k, path)}
                
        except ValueError as e:
            if "not enough values" in str(e):
                values = {}
            else:
                raise e
            
        # Return values packed in a dictionary.
        return values
    
    def getcalctype(self, file):
        """Takes a chemical computation file and gives the calc type labels, 
        based on the filename formulation: xxxxxxx_NSyyy.log, where x chars
        refer to the structure name, N is the iteration number, S is the spin
        state label, and yyy is the optimization type. 
        """
        labels = file.split('_')[-1]
        iter = int(labels[0])
        state = labels[1]
        type = labels.split('.')[0][2:]
        return (iter, state, type)
    
    def appendline(self, line):
        """Useful for writing log files.
        """
        with open(self.fn, 'a') as f:
            f.write(line + '\n')
    
    def files_end_with(self, suffix):
        """Returns a list of files ending with the given suffix.
        """
        return list(filter(
                        lambda file: file.endswith(suffix),
                        os.listdir(self.fn)
                        ))
    
    def tail(self, lines=1, _buffer=4098):
        """Tail a file and get X lines from the end"""
        with open(self.fn) as f:
        
            # place holder for the lines found
            lines_found = []

            # block counter will be multiplied by buffer
            # to get the block size from the end
            block_counter = -1

            # loop until we find X lines
            while len(lines_found) < lines:
                try:
                    f.seek(block_counter * _buffer, os.SEEK_END)
                except IOError:  # either file is too small, or too many lines requested
                    f.seek(0)
                    lines_found = f.readlines()
                    break

                lines_found = f.readlines()

                # we found enough lines, get out
                if len(lines_found) > lines:
                    break

                # decrement the block counter to get the
                # next X bytes
                block_counter -= 1

        return lines_found[-lines:]
    
    def head(self, lines=1):
        """Head a file and get X lines from the beginning"""
        with open(self.fn) as f:
            head = [next(f) for x in range(lines)]
        return head
    
    def lines(self):
        """Gives all lines from a file as a list"""
        with open(self.fn, "rt", encoding='latin-1') as f:
            lines = f.read().splitlines()
        return list(lines)
    
    def replace_vals(self, starttxt, endtxt, outfile):
        """Replaces all instances of starttxt with endtxt, printing the file as
        outfile.
        """
        with open(self.fn, "rt") as fin:
            with open(outfile, "wt") as fout:
                for line in fin:
                    fout.write(line.replace(starttxt, endtxt))
    
    def replace_all_vals(self, keydict, outfile):
        """Same as replace_vals, but takes a dictionary of old:new text 
        replacements as the key.
        """
        with open(self.fn, "rt") as fin:
            with open(outfile, "wt") as fout:
                for line in fin:
                    for old, new in keydict.items():
                        line = line.replace(old, new)
                    fout.write(line)