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
2. Load FRE into your environment by running `module load fre/bronx-16`
3. Type `cd fretransfer`, then `python3 fretransfer.py -h` for a list of options.  
   *assumes that the binary command for python v3.x is aliased to `python3`
4. Untar the test ascii, history, and restart files.
    `tar -xzvf tests/test_data/ascii/19820101_ascii_raw.tar.gz -C tests/test_data/ascii/`
    `tar -xzvf tests/test_data/history/19820101_history_raw.tar.gz -C tests/test_data/history/`
    `tar -xzvf tests/test_data/restart/19820109_restart_raw.tar.gz -C tests/test_data/restart/`
5. There are several scenarios for which to execute fretransfer. All examples below utilize history files, but can encompass ascii and restart files as well:

   * Scenario 1: Combine, tar, and transfer files from Gaea to GFDL
   Example: `python3 fretransfer.py -expName test_experiment -fileType history -sourceDir $PWD/tests/test_data/history/ -gfdlDir /path/to/GFDL/destination -combine -tar -compress -transfer -saveBatchOpts output=/path/for/combine-tar/job/file/stdout account=gfdl_YOURGROUPLETTER job-name=tar_combine_job mail-type=fail -xferBatchOpts output=/path/for/transfer/job/file/stdout account=gfdl_YOURGROUPLETTER job-name=transfer_job mail-type=fail -submit`
   
   * Scenario 2: Combine, no tar, and transfer files
   Note: Creates 2 separate batch jobs (outputStager and gcp) and saves them outside the sourceDir.
   Example: `python3 fretransfer.py -expName test_experiment -fileType history -sourceDir tests/test_data/history/ -gfdlDir /path/to/GFDL/destination -combine -transfer -saveBatchOpts output=/path/for/combine/job/file/stdout account=gfdl_YOURGROUPLETTER job-name=tar_combine_job mail-type=fail -xferBatchOpts output=/path/for/transfer/job/file/stdout account=gfdl_YOURGROUPLETTER job-name=transfer_job mail-type=fail -submit`
   
   * Scenario 3: Combine, no tar, no transfer
   Example: `python3 fretransfer.py -expName test_experiment -fileType history -sourceDir tests/test_data/history/ -gfdlDir /path/to/GFDL/destination -combine -saveBatchOpts output=/path/for/combine/job/file/stdout account=gfdl_YOURGROUPLETTER job-name=tar_combine_job mail-type=fail -submit`
   
   * Scenario 4: No combine, tar, transfer
   Example: `python3 fretransfer.py -expName test_experiment -fileType history -sourceDir history/ -gfdlDir /path/to/GFDL/destination -tar -compress -transfer -saveBatchOpts output=/path/for/tar/job/file/stdout account=gfdl_YOURGROUPLETTER job-name=tar_combine_job mail-type=fail -xferBatchOpts output=/path/for/transfer/job/file/stdout account=gfdl_YOURGROUPLETTER job-name=transfer_job mail-type=fail -submit`
   
   * Scenario 5: No combine, no tar, transfer
   Note: If a .tar file exists outside the sourceDir, fretransfer will natively call output.stager. If not (i.e. only combined files present, mixture of uncombined/combined, and desiring to transfer a directory of all uncombined files), fretransfer will create a gcp batch job and submit it.
   Example: `python3 fretransfer.py -expName test_experiment -fileType history -sourceDir history/ -gfdlDir /path/to/GFDL/destination -transfer -xferBatchOpts output=/path/for/transfer/job/file/stdout account=gfdl_YOURGROUPLETTER job-name=transfer_job mail-type=fail -submit`
   
   * Scenario 6: No combine, no tar, no transfer (dry run)
   Example: `python3 fretransfer.py -expName test_experiment -fileType history -sourceDir history/ -gfdlDir /path/to/GFDL/destination`
   
   * Scenario 7: Combine, tar, no transfer
   Example: `python3 fretransfer.py -expName test_experiment -fileType history -sourceDir history/ -gfdlDir /path/to/GFDL/destination -combine -tar -compress -saveBatchOpts output=/path/for/combine/job/file/stdout account=gfdl_YOURGROUPLETTER job-name=tar_combine_job mail-type=fail -submit`
   
   * Scenario 8: No combine, tar, no transfer
   Example: `python3 fretransfer.py -expName test_experiment -fileType history -sourceDir history/ -gfdlDir /path/to/GFDL/destination -tar -saveBatchOpts output=/path/for/combine/job/file/stdout account=gfdl_YOURGROUPLETTER job-name=tar_combine_job mail-type=fail -submit`
   Note: Only using '-tar' will create an uncompressed archive file. Use '-compress' for the vice versa. 

# Support or Contact
It you are having problems using the code, open an issue in the fretransfer repository:  
https://github.com/meteorologist15/fretransfer/issues
