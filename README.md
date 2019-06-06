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
   python3 fretransfer userDefs -expName mom6_solo_global_ALE_z -fileType history    
   -sourceDir /home/sourceDirectory -destDir /archive/Firstname.Lastname -destMachine gfdl 
   ```
4. Pass the shell variables defined by frerun to the history argFile generated in step 3:
   ```
    python3 fretransfer freDefs -actionSaveOn 1  -actionXferOn $?flagOutputXferOn [-more options]
   ```
# Support or Contact
It you are having problems using the code, open an issue in the fretransfer repository:  
https://github.com/wrongkindofdoctor/fretransfer/issues
