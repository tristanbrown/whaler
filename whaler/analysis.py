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
        elnums = [1, 3, 5, 2, 4]
        self.statekey = {
            self.states[i]:elnums[i] for i in range(len(elnums))}
        
        # Analysis output filenames. 
        self.gs_out = "groundstate_Es.csv"
        self.crude_out = "cruderxn_Es.csv"
        self.thermo_out = "thermo_Es.csv"
        
    def groundstates_all(self):
        """Compares the energies of each calculated spin state for a structure
        and writes the energy differences as a table."""
        
        print("Calculating ground spin states.")
        # Collect state energies from files. 
        results = [self.get_states(struct) for struct in self.structs]
        
        # Construct dataframe. 
        headers = np.array(self.states)
        gEs = (
            pd.DataFrame(data=results, index=self.structs, columns=headers))
        
        gEs['Ground State'] = gEs.idxmin(axis=1)
        
        return gEs
        
    def write_data(self, type):
        # Choose the data type and output location. 
        
        if type == "gs":
            out = self.gs_out
            try:
                os.remove(os.path.join(self.loc, out))
                print("Overwriting %s." % out)
            except:
                pass
            data = self.gEs
            message = "optimization energies and ground states"
        elif type == "cruderxn":
            out = self.crude_out
            data = self.crude_rxn_Es()
            message = "crude reaction energies"
        elif type == "thermo":
            out = self.thermo_out
            data = self.therm_Es
            message = "thermodynamic values"
        else:
            raise
        
        # Write the data.
        
        data.to_csv(os.path.join(self.loc, out))
        print("Wrote {0} to {1}.".format(message, out))
    
    @property
    def gEs(self):
        """Returns self.gEs, either from the existing assignment, from the
        output file, or from a fresh calculation. 
        """
        try:
            return self._gEs
        except AttributeError:
            try:
                self._gEs = pd.read_csv(
                            os.path.join(self.loc, self.gs_out),
                            index_col=0)
                print("Reading ground spin states from %s." % self.gs_out)
            except OSError:
                self._gEs = self.groundstates_all()
            return self._gEs
        
    def crude_rxn_Es(self):
        """Subtracts the crude (geo) energy of each M2(L)4 structure and N2 from
        the corresponding M2(L)4N and M2(L)4N2 structures, tabulating the
        results.
        """
        # Make a dictionary of all structures with ground state energies. 
        short_gEs = self.gEs.dropna(axis=0, how='all')
        struct_Es = {
            struct : short_gEs.loc[struct][:-1].min()
            for struct in short_gEs.index}
        
        # Calculate the energy differences. 
        structs = []
        nitride = []
        nitrogen = []
        
        N2_E = self.finalE("N2_4geo.log", os.path.join(self.loc, "N2"))
        
        for k,v in struct_Es.items():
            structs.append(k)
            try:
                nitride.append(struct_Es[k + 'N'] - v - N2_E/2)
            except:
                nitride.append(np.nan)
            try:
                nitrogen.append(struct_Es[k + 'N2'] - v - N2_E)
            except:
                nitrogen.append(np.nan)
        
        # Tabulate the data. 
        headers = ['Add N', 'Add N2']
        results = np.array([nitride, nitrogen]).T
        rxn_Es = pd.DataFrame(data=results, index=structs, columns=headers)
        rxn_Es = rxn_Es.dropna(axis=0, how='all')
        
        print(rxn_Es)
        return rxn_Es
    
    @property
    def therm_Es(self):
        """Returns self.therm_Es, either from the existing assignment, from the
        output file, or from a fresh calculation. 
        """
        try:
            return self._therm_Es
        except AttributeError:
            try:
                self._therm_Es = pd.read_csv(
                            os.path.join(self.loc, self.thermo_out),
                            index_col=0)
                print("Reading thermodynamic values from %s."
                        % self.thermo_out)
            except OSError:
                self._therm_Es = self.thermo_all()
            return self._therm_Es
    
    def thermo_all(self):
        """Compares the energies of each calculated spin state for a structure
        and writes the energy differences as a table."""
        
        print("Calculating thermodynamic values.")
        # Collect state energies from files. 
        results = [self.getthermo(struct) for struct in self.structs]
        
        # Construct dataframe. 
        headers = np.array(self.states) # change this
        thermoEs = (
            pd.DataFrame(data=results, index=self.structs, columns=headers))
        
        # thermoEs['Ground State'] = gEs.idxmin(axis=1)
        
        return thermoEs
    
    def get_states(self, structure):
        """Returns a dictionary of energies of the various spin states for a
        structure, using all available distinct spin-state calculations. 
        """
        dir = IO(dir=os.path.join(self.loc, structure))
        return dir.get_values(
                structure, "geo.log", self.geovalid, self.finalE)
    
    def get_thermo(self, structure):
        """Returns a dictionary of thermodynamic values for a structure, using all available distinct spin-state calculations. 
        """
        dir = IO(dir=os.path.join(self.loc, structure))
        return dir.get_values(
                structure, "freq.log", self.freqvalid, self.thermo_E)
    
        
    def write_inp_all(self, type, template):
        """Used for writing input files based on previous calculations that 
        generate .xyz and .gbw files. 
        """
        
        for struct in self.structs:
            try:
                state = self.gEs.loc[struct,'Ground State']
                if state in self.states:
                    self.assemble_inp(struct, template, state, type)
            except KeyError:
                print("Ground state missing for %s. Rerun whaler gs." % struct)
        
    def write_inp(self, struct, template, state, coords, filename, gbw=None):
        """
        """
        path = os.path.join(self.loc, struct)
        outfile = os.path.join(path, filename)
        
        # Choose the state number. 
        statenum = self.statekey[state]
        
        # Read the template. Plug values into the template.
        if os.path.exists(outfile.split('.')[0] + ".gbw"):
            message = ("Skipping %s"
                        " because it has already been used in a calculation."
                        % filename)
            
        else:
            reader = IO(template, self.loc)
            
            replacekey = {
                            "[struct]":struct,
                            "[spin]":str(statenum),
                            "[coords]":"\n".join(coords)}
            if gbw is None:
                replacekey["MOREAD"] = "#MOREAD"
                replacekey["%moinp"] = "# %moinp"
            else:
                replacekey["[gbw]"] = gbw
            
            reader.replace_all_vals(replacekey, outfile)
            message = "Wrote " + filename + "."
        
        print(message)
        self.logfile.appendline(message)
    
    def assemble_inp(self, struct, template, state, type):
        """
        """
        # Get the xyz coordinates for the input file. 
        xyzfile, coords = self.get_xyz(struct, state, state + "geo")
        
        # Make the filename.
        filename = xyzfile.split("geo")[0] + type + ".inp"
        
        # Find the gbw file.
        gbw = xyzfile.split(".")[0] + ".gbw"
        
        # Write the .inp file.
        if coords != []:
            self.write_inp(struct, template, state, coords, filename, gbw)
        
    def get_xyz(self, struct, state, type="start"):
        """
        """
        path = os.path.join(self.loc, struct)
        dir = IO(dir=path)
        
        # Filter down to the appropriate .xyz file. 
        xyzfile = sorted(dir.files_end_with(type + ".xyz"))[-1]
        
        # Check if the .xyz file has been aligned. 
        if self.xyz_aligned(xyzfile, path):
            reader = IO(xyzfile, path)
            return (xyzfile, reader.lines()[2:])
        else:
            return (xyzfile, [])
    
    def xyz_aligned(self, filename, dir):
        """
        """
        reader = IO(filename, dir)
        xyzhead = reader.head(3)
        if 'Coordinates' in xyzhead[1]:
            message = filename + ' needs alignment.'
            print(message)
            self.logfile.appendline(message)
            return False
        elif len(xyzhead[2]) == 49:
            return True
        else:
            message = filename + ' has unknown structure.'
            print(message)
            self.logfile.appendline(message)
            return False
    
    def geovalid(self, file, path):
        """
        """
        return self.isvalid(file, path) and self.geoconverged(file, path)
    
    def freqvalid(self, file, path):
        """
        """
        reader = IO(file, path)
        
        return self.isvalid(file, path) and self.freqconverged(file, path)
    
    def freqconverged(self, file, path, chunk=10000, maxsearch=100000):
        """
        """
        reader = IO(file, path)
        tail = reader.tail(chunk)
        print(tail)
    
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
    
    def geoconverged(self, file, path, chunk=100, maxsearch=1000):
        """
        """
        reader = IO(file, path)
        tail = reader.tail(chunk)
        if chunk > maxsearch:
            self.logfile.appendline(file + ' has unknown structure.')
            return False
        elif 'WARNING!!!!!!!\n' in tail:
            self.logfile.appendline(file + ' has not converged.')
            return False
        elif '*** OPTIMIZATION RUN DONE ***' in ''.join(tail):
            return True
        else:
            self.geoconverged(file, path, chunk*2)
        
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