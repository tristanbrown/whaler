"""A module containing analytical objects specific to a particular experiment. 
"""
import os
import numpy as np
import pandas as pd
from whaler.analysis import Analysis

class Reactions():
    """
    """
    def __init__(self):
        self.A = Analysis()
        
        # Analysis output filenames. 
        self.crude_N2_out = "crudeN2_Es.csv"
        self.N2_act_out = "N2_act_Es.csv"
        self.N2_bond_out = "N2_act_bonds.csv"
        
        # Physical constants.
        self.kB = 3.1668114/1000000
        self.temp = 298.15
    
    def write_crude_N2(self):
        """
        """
        self.A.write_data("cruderxn", self.crude_N2_out, self.crude_N2_act())
    
    def write_N2_act(self):
        """
        """
        self.A.write_data("N2act", self.N2_act_out, self.therm_N2_act())
    
    def write_N2_bonds(self):
        """
        """
        self.A.write_data("bonds", self.N2_bond_out, self.MMN2_bonds())
    
    def MMN2_bonds(self):
        """Tabulates the M-M, M-N, and N-N bond lengths in M2(L)4, M2(L)4N, and 
        M2(L)4N2 structures. 
        """
        # Generate structure sets.
        short_gEs = self.A.gEs.dropna(axis=0, how='all')
        base_structs = {
            struct : short_gEs.loc[struct, 'Ground State']
            for struct in short_gEs.index if struct[-1] == '4'
            }
        N_structs = {
            struct : short_gEs.loc[struct, 'Ground State']
            for struct in short_gEs.index if struct[-2:] == '4N'
            }
            
        N2_structs = {
            struct : short_gEs.loc[struct, 'Ground State']
            for struct in short_gEs.index if struct[-2:] == 'N2'
            }
        
        print(base_structs)
        print(N_structs)
        print(N2_structs)
        
        gs_M_M = {
            # struct : 
            }
        
        return []
    
    def crude_N2_act(self):
        """Subtracts the crude (geo) energy of each M2(L)4 structure and N2 from
        the corresponding M2(L)4N and M2(L)4N2 structures, tabulating the
        results.
        """
        # Make a dictionary of all structures with ground state energies. 
        short_gEs = self.A.gEs.dropna(axis=0, how='all')
        struct_Es = {
            struct : short_gEs.loc[struct][:-1].min()
            for struct in short_gEs.index}
        
        # Calculate the energy differences. 
        structs = []
        nitride = []
        nitrogen = []
        
        N2_E = self.A.finalE("N2_4geo.log", os.path.join(self.A.loc, "N2"))
        
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
        
    def therm_N2_act(self):
        """Subtracts the thermodynamically-corrected energy of each M2(L)4
        structure and N2 from the corresponding M2(L)4N and M2(L)4N2 structures, tabulating the results.
        """
        # Calculate G for all of the structures.
        therm = self.A.therm_Es.dropna(axis=0, how='all')
        
        therm['Symm #'] = [self.symm(struct) for struct in therm.index]
        
        # S (rot) = kB*T(ln(qrot/sn)+N), N = 1, 1.5
        therm['S*T (rot)'] = (
            self.kB * self.temp *
            (np.log(therm['qrot']/therm['Symm #']) + therm['rot #'])
            )
        
        therm['S*T (tot)'] = (
            therm['S*T (el)'] + therm['S*T (vib)'] + therm['S*T (trans)']
            + therm['S*T (rot)']
            )
        
        # G = H - T*S
        therm['G'] = therm['H'] - therm['S*T (tot)']
        
        print(therm)
        
        # Calculate the energy differences. 
        structs = []
        nitride = []
        nitrogen = []
        
        N2_G = therm.loc['N2','G']
        
        for base in therm.index:
            structs.append(base)
            base_G = therm.loc[base, 'G']
            try:
                nitride.append(therm.loc[base + 'N', 'G'] - base_G - N2_G/2)
            except KeyError:
                nitride.append(np.nan)
            try:
                nitrogen.append(therm.loc[base + 'N2', 'G'] - base_G - N2_G)
            except KeyError:
                nitrogen.append(np.nan)
        
        # Tabulate the data. 
        headers = ['Add N', 'Add N2']
        results = np.array([nitride, nitrogen]).T
        rxn_Es = pd.DataFrame(data=results, index=structs, columns=headers)
        rxn_Es = rxn_Es.dropna(axis=0, how='all')
        
        print(rxn_Es)
        return rxn_Es
    
    def symm(self, structure):
        """Gives the symmetry numbers for N2, M2(L)4, M2(L)4N, and M2(L)4N2.
        """
        sn = 1
        if 'N2' in structure:
            sn = sn*2
        if 'OO4' in structure:
            sn = sn*4*2*3*3*3*3
        if '2N' in structure:
            sn = sn*4*3*3*3*3
        
        return sn