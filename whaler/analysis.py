"""
 
"""
import time
import os
import numpy as np
import pandas as pd
from .dataprep import IO
from .dataprep import extract_floats as extr
from .dataprep import dict_values as dvals

class Analysis():
    """
    """
    def __init__(self):
        self.loc = os.getcwd()
        self.structs = next(os.walk('.'))[1]
        self.logfile = IO('whaler.log', self.loc)
        self.states = ['S', 'T', 'P', 'D', 'Q']
        self.spinflip = {
            'S' : 'T',
            'T' : 'S',
            'D' : 'Q',
            'Q' : 'D'
            }
        self.thermvals = [
            'U', 'H', 'S*T (el)', 'S*T (vib)', 'S*T (trans)', 'qrot', 'rot #']
        elnums = [1, 3, 5, 2, 4]
        self.statekey = {
            self.states[i]:elnums[i] for i in range(len(elnums))}
        
        # Analysis output filenames. 
        self.gs_out = "groundstate_Es.csv"
        self.crude_out = "cruderxn_Es.csv"
        self.thermo_out = "thermo_Es.csv"
        
    def write_data(self, type, custom_out=None,
                        custom_data=None, format=None):
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
        elif type == "thermo":
            out = self.thermo_out
            try:
                os.remove(os.path.join(self.loc, out))
                print("Overwriting %s." % out)
            except:
                pass
            data = self.therm_Es
            message = "thermodynamic values"
        elif type == "bonds":
            out = custom_out
            data = custom_data
            message = "bond lengths"
        elif type == "cruderxn":
            out = custom_out
            data = custom_data
            message = "crude reaction energies"
        elif type == "N2act":
            out = custom_out
            data = custom_data
            message = "reaction energies"
        else:
            raise
        
        # Write the data.
        
        data.to_csv(os.path.join(self.loc, out), float_format=format)
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
    
    def thermo_all(self):
        """Compares the energies of each calculated spin state for a structure
        and writes the energy differences as a table."""
        
        print("Calculating thermodynamic values.")
        # Collect thermodynamic values from files. 
        results = dvals([self.get_thermo(struct) for struct in self.structs])
        
        # Construct dataframe. 
        headers = np.array(self.thermvals)
        thermoEs = (
            pd.DataFrame(data=results, index=self.structs, columns=headers))
        
        # thermoEs['Ground State'] = gEs.idxmin(axis=1)
        # print(thermoEs)
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
        values = dir.get_values(
                structure, "freq.log", self.freqvalid, self.thermo_vals)
        
        return values
    
        
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
        xyzfile, coords = self.get_xyz(struct, state, "geo")
        
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
        xyzfile = sorted(dir.files_end_with(state + type + ".xyz"))[-1]
        
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
    
    def xyz_to_coords(self, xyz):
        """Converts a list of .xyz file lines into a list of atom-labeled
        coordinates.
        """
        coords = []
        for line in xyz:
            rawcoord = line.split()
            coord = [rawcoord[0]] + [float(n) for n in rawcoord[1:]]
            coords.append(coord)
        
        return coords
    
    def bondlength(self, struct, state, elem1, elem2, axis='z', skip=0):
        """
        """
        axiskey = {'x':1, 'y':2, 'z':3}
        
        # Get the coordinates. 
        file, rawcoords = self.get_xyz(struct, state, "geo")
        coords = self.xyz_to_coords(rawcoords)
        
        if coords == []:
            print("Can't get coordinates from %s." % file)
            return None
        else:
        
            # Find the atoms of the right elements. 
            elems = [elem1, elem2]
            for i in range(2):
                if elems[i] == 'M':
                    elems[i] = coords[0][0]
            
            atomlist = [atom for atom in coords if atom[0] in elems]
            
            # Eliminate skipped atoms. 
            for x in range(skip):
                axis_coord = list(zip(*atomlist))[axiskey[axis]]
                maxindex = axis_coord.index(max(axis_coord))
                del atomlist[maxindex]
            
            # Choose the 2 atoms furthest along the given axis.
            atoms = []
            for elem in elems:
                axis_max = -99999
                maxindex = None
                for i,atom in enumerate(atomlist):
                    if atom[0] == elem and atom[axiskey[axis]] > axis_max:
                        axis_max = atom[axiskey[axis]]
                        maxindex = i
                atoms.append(np.array(atomlist.pop(maxindex)[1:]))
            
            # Calculate the bond length. 
            length = np.sqrt(np.sum((atoms[0] - atoms[1])**2))
            
            return length
    
    def geovalid(self, file, path):
        """
        """
        return self.isvalid(file, path) and self.geoconverged(file, path)
    
    def freqvalid(self, file, path):
        """
        """
        return self.isvalid(file, path) and self.freqconverged(file, path)
    
    def isvalid(self, file, path):
        """
        """
        reader = IO(file, path)
        end = reader.tail(2)
        if 'ABORTING THE RUN\n' in end:
            message = file + ' aborted abnormally.'
            self.logfile.appendline(message)
            print(message)
            return False
        elif 'ORCA TERMINATED NORMALLY' in end[0]:
            return True
        else:
            message = file + ' has unknown structure.'
            self.logfile.appendline(message)
            print(message)
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
    
    def freqconverged(self, file, path):
        """
        """
        reader = IO(file, path)
        lines = reader.lines()
        if ("ORCA_NUMFREQ: ORCA finished with an error in the energy"
            " calculation") in lines:
            print("SCF convergence error in %s." % file)
            return False
        else:
            return True
        
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
    
    def thermo_vals(self, file, path, chunk=100):
        """Extracts the thermodynamic values from a .log file. 
        """
        reader = IO(file, path)
        # print("Thermodynamic values can be extracted from %s." % file)
        lines = reader.lines()
        
        # Mark the data locations.
        marker1 = 'VIBRATIONAL FREQUENCIES'
        marker2 = 'NORMAL MODES'
        marker3 = 'INNER ENERGY'
        for i in range(len(lines)):
            line = lines[i]
            if line == marker1:
                vib_start = i+3
            elif line == marker2:
                vib_end = i-3
            elif line == marker3:
                therm_start = i
        
        # Extract the data values. 
        vib_lines = lines[vib_start:vib_end]
        U = extr(lines[therm_start+19])[0]
        H = extr(lines[therm_start+39])[0]
        S_el = extr(lines[therm_start+54])[0]
        S_vib = extr(lines[therm_start+55])[0]
        S_trans = extr(lines[therm_start+57])[0]
        linearity = lines[therm_start+65]
        if ' linear' in linearity:
            rot_num = 1
        elif 'nonlinear' in linearity:
            rot_num = 1.5
        else:
            raise
        qrot = extr(lines[therm_start+68])[0]
        
        vibs = [extr(line)[:2] for line in vib_lines]
        img_modes = []
        for vib in vibs:
            if vib[1] < 0:
                img_modes.append(vib)
        
        if len(img_modes) > 0:
            values = {}
            print("ERROR: %s contains imaginary modes:" % file)
            for mode in img_modes:
                print("#{0}: {1} cm^-1".format(mode[0], mode[1]))
        else:
            values = {
                'U':U, 'H':H, 'S*T (el)':S_el, 'S*T (vib)':S_vib,
                'S*T (trans)':S_trans, 'qrot':qrot, 'rot #':rot_num}

        return values
    
    