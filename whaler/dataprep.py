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
    
    def load_array_with_labels(self, delim=',', datatype='int',
                                    coltype='str', rowtype='str'):
        """Used for extracting data from text files with row and column labels.
        Returns a tuple containing 3 arrays: the data, the column labels,
        and the row labels.
        
        The optional arguments allow the user to choose the delimiter, as well
        as specifying the types for the labels and data. 
        """
        with open(self.fn, 'r') as f:
            col_labels = np.array(f.readline().split(delim)[1:], dtype=coltype)
        num_col = len(col_labels)
        row_labels = np.genfromtxt(self.fn, delimiter=delim, dtype=rowtype, 
                                skip_header=1, usecols=0)
        data = np.genfromtxt(self.fn, delimiter=delim, dtype=datatype, 
                                skip_header=1, usecols=range(1, num_col+1))
        
        return (data, col_labels, row_labels)
        
    def load_arb_rows(self, delim=',', type='int', skipcol=0):
        """Used for extracting data from text files with labeled rows of
        arbitrary length. 
        Returns a list of the first item from each row, and a list of numpy
        arrays of the remaining items.
        """
        with open(self.fn, 'r') as f:
            labels = []
            rows = []
            for row in f.readlines():
                values = re.split(delim+'|\n', row)[:-1]
                labels.append(values[0])
                rows.append(np.array(values[1+skipcol:], dtype=type))
        return (np.array(labels), rows)
    
    def tabulate_data(self, columns, headers, sortby=None):
        """Takes a list of data columns, a list of column headers, and a header
        name to sort the columns. Writes a complete data table to a .csv file. 
        """
        formatted = []
        for col in columns:
            if col.dtype == 'float':
                formatted.append(["%.3f" % num for num in col])
            else:
                formatted.append(col)
                
        table = np.array(formatted).T
        try:
            sortindex = headers.index(sortby)
            table = table[columns[sortindex].argsort()[::-1]]
        except:
            print("No valid column to sort by.")
            
        np.savetxt(self.fn, table, fmt='%s', delimiter=',', newline='\n', 
                        header=(','.join(headers)), comments='')
    
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
        with open(self.fn) as f:
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