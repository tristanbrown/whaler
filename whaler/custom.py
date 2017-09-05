"""
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
        self.thermo_N2_out = "N2_thermo_Es.csv"
    
    def write_crude_N2(self):
        """
        """
        self.A.write_data("cruderxn", self.crude_N2_out, self.crude_N2_act())
    
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