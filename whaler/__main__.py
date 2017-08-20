"""
Main routine of whaler. 
"""

import sys
from whaler import config

def main(args=None):
    
    # Determine filenames.
    
    if args is None:
        args = sys.argv[1:]
    
    if len(args) == 0:
        print("No arguments passed.")
    
    
if __name__ == "__main__":
    main()