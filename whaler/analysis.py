"""
 
"""

import os
import numpy as np
from whaler.dataprep import IO

class Analysis():
    """
    """
    def __init__(self):
        self.loc = os.getcwd()
        self.structs = next(os.walk('.'))[1]
        self.logfile = IO('whaler.log', self.loc)
        
    def groundstates_all(self, outname="groundstates.csv"):
        """Compares the energies of each calculated spin state for a structure
        and writes the energy differences as a table."""
        
        results = [self.spinstates(struct) for struct in self.structs]
        columns = [] #turn list of rows into list of columns
        
        # write table as groundstates.out file. 
        writer = IO(outname, self.loc)
        
        
        headers = np.array(['Structures', 'S', 'T', 'P', 'D', 'Q'])
        
        writer.tabulate_data(columns, headers, 'Structures')
        
    def spinstates(self, structure):
        """For a given structure, identifies all of the files optimizing 
        geometries in different spin states. Verifies convergence, and then
        finds the final single-point energy for each file. Returns an array of 
        energies of the various spin states.
        Possibilities: S T P D Q (for S = 0, 1, 2, 1/2, 3/2)
        """
        path = os.path.join(self.loc, structure)
        geologs = list(filter(
                        lambda file: self.isfiletype(file, path, "geo.log"),
                        os.listdir(path)
                        ))
        print(geologs)
    
    def isfiletype(self, file, path, suffix):
        """
        """
        return file.endswith(suffix) and self.isvalid(file, path)
    
    def isvalid(self, file, path):
        """
        """
        reader = IO(file, path)
        end = reader.tail(2)
        if 'ABORTING THE RUN\n' in end:
            self.logfile.appendline(file + ' aborted abnormally.')
            return False
        elif 'ORCA TERMINATED NORMALLY' in end[0]:
            return True
        else:
            self.logfile.appendline(file + ' has unknown structure.')
            return False
    
    def getcalctype(self, file):
        """Takes a chemical computation file and gives the calc type labels, 
        based on the filename formulation: xxxxxxx_NSyyy.log, where x chars
        refer to the structure name, N is the iteration number, S is the spin
        state label, and yyy is the optimization type. 
        """
        return ''