"""
Main routine of whaler. 
"""

import sys
from whaler import config
from whaler import analysis

def main(args=None):
    
    # Determine filenames.
    
    if args is None:
        args = sys.argv[1:]
    
    A = analysis.Analysis()
    
    if len(args) == 0:
        print("No arguments passed.")
    elif 'gs' in args:
        A.groundstates_all()
    
    
if __name__ == "__main__":
    main()