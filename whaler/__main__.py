"""
Main routine of whaler. 
"""

import sys
from whaler import config
from whaler import analysis
from whaler import filegen

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
    elif 'cruderxn' in args:
        A = analysis.Analysis()
        A.write_data("cruderxn")
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
    
if __name__ == "__main__":
    main()