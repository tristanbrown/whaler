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
    
    
    
    if len(args) == 0:
        print("No arguments passed.")
    elif 'gs' in args:
        A = analysis.Analysis()
        A.groundstates_all()
        A.write_gsEs()
    elif 'freqinp' in args:
        A = analysis.Analysis()
        A.write_inp_all("freq", "freqsample.inp")
    elif 'singleinp' in args:
        A = analysis.Analysis()
        A.write_inp_all("single", "singlesample.inp")
    elif 'filegen' in args:
        gen = filegen.Generator(args[-1])
        gen.run()
    
if __name__ == "__main__":
    main()