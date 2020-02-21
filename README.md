# Fretransfer
This repository contains fretransfer scripts that generate argument files (``argfiles``) for raw (un-tarred) history, restart, and ascii model output files, and call output.stager to process the argfiles.
# Requirements
* Python v3.5 or later
* Python modules:
  * argparse
  * configparser
  * datetime
  * fnmatch
  * glob
  * logging
  * os
  * re
  * shutil
  * stat
  * subprocess
  * sys
* supported version of FRE
# Quickstart
1. open a terminal and clone the repository
   `git clone git@github.com:meteorologist15/fretransfer.git`
   `git clone https://github.com/meteorologist15/fretransfer.git`
2. Load FRE into your environment by running `module load fre/<latest_fre_version>`
3. Type `cd fretransfer`, then `python3 fretransfer -h` for a list of options.  
   *assumes that the binary command for python v3.x is aliased to `python3`
4. There are several scenarios to execute fretransfer:
   




5. To run fretransfer on history files with required arguments:  
   ```
   module load fre/bronx-<latest version number>
   python3 fretransfer.py -expName mom6_solo_global_ALE_z -fileType history    
   -sourceDir /path/to/history/directory -gfdlDir /path/to/GFDL/destination -
   ```
   where `fileType` is _ascii_ and/or _history_ and/or _restart_ (yes, you can run the script on all three file types at once)  
   `expName` is the name of the experiment that generated the output files  
   `sourceDir` is the directory with RESTART, HISTORY, and ASCII directories that contain the files to transfer  
   `destDir` is the root directory of the machine where the files will be transferred  
   `destMach` is the machine you are moving the files to (`gaea` and `gfdl` are currently supported)  
   `groupAccount` is the name of your gfdl group account  
 
# Support or Contact
It you are having problems using the code, open an issue in the fretransfer repository:  
https://github.com/wrongkindofdoctor/fretransfer/issues
