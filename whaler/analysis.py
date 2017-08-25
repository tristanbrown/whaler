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
        print(self.loc)
        print(self.structs)
        
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
        