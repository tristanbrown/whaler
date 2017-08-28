"""
 
"""
import time
import os
import numpy as np
import pandas as pd
from whaler.dataprep import IO

class Analysis():
    """
    """
    def __init__(self):
        self.loc = os.getcwd()
        self.structs = next(os.walk('.'))[1]
        self.logfile = IO('whaler.log', self.loc)
        self.states = ['S', 'T', 'P', 'D', 'Q']
        
    def groundstates_all(self):
        """Compares the energies of each calculated spin state for a structure
        and writes the energy differences as a table."""
        
        # Collect state energies from files. 
        results = [self.spinstates(struct) for struct in self.structs]
        
        # Construct dataframe. 
        headers = np.array(self.states)
        self.gEs = (
            pd.DataFrame(data=results, index=self.structs, columns=headers))
        
        self.relgEs = self.gEs.subtract(self.gEs.min(1), axis=0)
        self.gEs['Ground State'] = self.gEs.idxmin(axis=1)
        self.relgEs['Ground State'] = self.gEs['Ground State']
        
    def write_gsEs(self, outname="groundstate_Es.csv", 
                            diffname="groundstate_relEs.csv"):
        # Write the ground state data.
        self.gEs.to_csv(os.path.join(self.loc, outname))
        self.relgEs.to_csv(os.path.join(self.loc, diffname))
        
    
    
    def spinstates(self, structure):
        """For a given structure, identifies all of the files optimizing 
        geometries in different spin states. Verifies convergence, and then
        finds the final single-point energy for each file. Returns an array of 
        energies of the various spin states.
        Possibilities: S T P D Q (for S = 0, 1, 2, 1/2, 3/2)
        """
        path = os.path.join(self.loc, structure)
        files = os.listdir(path) # Starting file list. 
        
        # Narrows it down to geo.log files.
        geologs = list(filter(
                        lambda file: file.endswith("geo.log"),
                        files
                        ))
        
        # Unpacks filetypes.
        ftypes = {file:self.getcalctype(file) for file in geologs}
        
        try:
            iter, state, type = (zip(*ftypes.values()))
            # Removes invalid and outdated files, marking the log. 
            curriter = max(iter)

            stateEs = {
                v[1]:self.finalE(k, path) for (k,v) in ftypes.items() 
                if v[0] == curriter and self.isvalid(k,path)}
                
        except ValueError:
            stateEs = {}
            
        # Define States and return full array of energies of states.
        return [
            stateEs[s] if s in stateEs.keys()
                else np.nan for s in self.states]
        
    def write_freqinp_all(self, template="freqsample.inp"):
        """
        """
        # Make sure self.gEs exists.
        try: 
            self.gEs
        except:
            try:
                self.gEs = pd.read_csv(
                            os.path.join(self.loc, "groundstate_Es.csv"),
                            index_col=0)
            except:
                print("Calculating ground spin states.")
                self.groundstates_all()
        
        for struct in self.structs:
            state = self.gEs.loc[struct,'Ground State']
            if state in self.states:
                self.write_freqinp(struct, template, state)
        
    def write_freqinp(self, struct, template, state):
        """
        """
        
        
        print(struct, state)
    
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
    
    def isvalid(self, file, path):
        """
        """
        reader = IO(file, path)
        end = reader.tail(2)
        if 'ABORTING THE RUN\n' in end:
            self.logfile.appendline(file + ' aborted abnormally.')
            return False
        elif 'ORCA TERMINATED NORMALLY' in end[0]:
            return self.isconverged(file, path)
        else:
            self.logfile.appendline(file + ' has unknown structure.')
            return False
    
    def isconverged(self, file, path, chunk=100):
        """
        """
        reader = IO(file, path)
        tail = reader.tail(chunk)
        if chunk > 1000:
            self.logfile.appendline(file + ' has unknown structure.')
            return False
        elif 'WARNING!!!!!!!\n' in tail:
            self.logfile.appendline(file + ' has not converged.')
            return False
        elif '*** OPTIMIZATION RUN DONE ***' in ''.join(tail):
            return True
        else:
            self.converged(file, path, chunk+100)
        
    def finalE(self, file, path, chunk=100):
        """Extracts the final Single Point Energy from a .log file. 
        """
        reader = IO(file, path)
        tail = reader.tail(chunk)
        marker = 'FINAL SINGLE POINT ENERGY'
        energyline = [s for s in tail if marker in s]
        if chunk > 1000:
            self.logfile.appendline(file + ': cannot find final energy.')
            return np.nan
        elif energyline == []:
            return self.finalE(file, path, chunk+100)
        else:
            return float(energyline[-1].split()[-1])