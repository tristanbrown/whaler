"""
Main routine of whaler. 
"""

import sys
import config

def main(args=None):
    
    # Determine filenames.
    
    if args is None:
        args = sys.argv[1:]
 
    out_name = 'results.csv' #check argparse
    
    # Analyze the data and write the results.
    
    
if __name__ == "__main__":
    main()