# whaler
Analysis software for the output files of ORCA (computational chemistry software)

# Installation and dependencies
Above the directory containing setup.py, install using:
    >>pip install whaler

This software has been tested in an Anaconda environment containing the 
following packages and their respective dependencies:
- python (v. 3.6.1)
- numpy
- pandas

# Usage
Currently, the package can be run from any directory as follows:

    >> whaler <params>

The general <params> available are:
    >> filegen (generation of geo.inp files and their parent directories)
    >> gs (calculation of ground states)
    >> freqinp (generation of frequency calculation input files from geo results)
    >> singleinp (like freqinp, but for single-point inputs)
    >> thermo (extraction of thermodynamic parameters from freq output)
    
The custom <params> available, relevant to the 2M2 + N2 -> 2M2N reaction are:
    >> N2bonds (calculation of relevant bond lengths)
    >> crudeN2 (calculation of reaction energies from geo.log energies)
    >> N2act (proper thermodynamic calculation of reaction energies)
    
All folders in the current directory will be considered in the analysis. 
config.py is meant to be easily edited by the user. 

# Options