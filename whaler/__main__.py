"""
Main routine of whaler. 
"""

import sys
from whaler import config
from whaler import analysis
from whaler import filegen
from whaler import custom

def main(args=None):
    
    # Determine filenames.
    
    if args is None:
        args = sys.argv[1:]
    
    # Check for requested analysis or file manipulation. 
    
    if len(args) == 0:
        print("No arguments passed.")
    elif 'gs' in args:
        A = analysis.Analysis()
        A.write_data("gs")
    elif 'freqinp' in args:
        A = analysis.Analysis()
        A.write_inp_all("freq", "freqsample.inp")
    elif 'singleinp' in args:
        A = analysis.Analysis()
        A.write_inp_all("single", "singlesample.inp")
    elif 'thermo' in args:
        A = analysis.Analysis()
        A.write_data("thermo")
    elif 'filegen' in args:
        gen = filegen.Generator(args[-1])
        gen.run()
    elif 'crudeN2' in args:
        A = custom.Reactions()
        A.write_crude_N2()
    elif 'N2act' in args:
        A = custom.Reactions()
        A.write_N2_act()
    elif 'N2bonds' in args:
        A = custom.Reactions()
        A.write_N2_bonds()
        
if __name__ == "__main__":
    main()