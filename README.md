# Fretransfer
This repository contains fretransfer scripts that generate argument files (``argfiles``) for raw (un-tarred) history, restart, and ascii model output files, and call output.stager to process the argfiles.
# Requirements
* Python v3.5 or later
* Python modules:
  * argparse
  * datetime
  * fnmatch
  * glob
  * os
  * re
  * shutil
  * subprocess
  * sys
# Quickstart
1. open a terminal and clone the repository  
   `git clone git@github.com:wrongkindofdoctor/fretransfer.git` or  
   `git clone https://github.com/wrongkindofdoctor/fretransfer.git`
2. type `cd fretransfer`, then `python3 fretransfer -help` for a list of options.  
   *assumes that the binary command for python v3.x is aliased to `python3`
3. To run fretransfer on history files with required arguments:  
   ```
   python3 fretransfer.py userDefs -expName mom6_solo_global_ALE_z -fileType history    
   -sourceDir /home/sourceDirectory -destDir /archive/Firstname.Lastname -destMach gfdl -groupAccount gfdl_<your group letter>
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
