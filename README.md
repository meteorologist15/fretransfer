# Fretransfer
Fretransfer is a tool that utilizes part of GFDL's Flexible Modeling System Runtime Environment (FRE) to selectively combine, compress, archive, and transfer raw netCDF files generated by GFDL model simulations as well as other files, all branded as either 'ascii' files, 'history' files, or 'restart' files. It allows for the flexible creation of '.args' files, state files used by the FRE workflow, which are referenced by FRE's output.stager script to set up the above tasks through Slurm batch jobs.
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
1. Open a terminal on Gaea and clone the repository
   (ssh) `git clone git@github.com:NOAA-GFDL/fretransfer.git`
   (https) `git clone https://github.com/NOAA-GFDL/fretransfer.git`
2. Load FRE into your environment 
   `module load fre/bronx-16`
3. Type `cd fretransfer`, then `python3 fretransfer.py -h` for a list of options.  
   *assumes that the binary command for python v3.x is aliased to `python3`
4. Untar the test ascii, history, and restart files.
    `tar -xzvf tests/test_data/ascii/19820101_ascii_raw.tar.gz -C tests/test_data/ascii/`
    `tar -xzvf tests/test_data/history/19820101_history_raw.tar.gz -C tests/test_data/history/`
    `tar -xzvf tests/test_data/restart/19820109_restart_raw.tar.gz -C tests/test_data/restart/`
5. The following 8 scenarios can be used to execute fretransfer. All examples below utilize history files, but can encompass ascii and restart files as well (note: all file paths must be absolute paths):

   * Scenario 1: Combine, tar, and transfer files from Gaea to GFDL
   Example: `python3 fretransfer.py -expName test_experiment -fileType history -sourceDir $PWD/tests/test_data/history/ -gfdlDir /path/to/GFDL/destination/ -combine -tar -compress -transfer -saveBatchOpts account=gfdl_YOURGROUPLETTER job-name=tar_combine_job mail-type=fail -xferBatchOpts account=gfdl_YOURGROUPLETTER job-name=transfer_job mail-type=fail -submit`
   
   * Scenario 2: Combine, no tar, and transfer files
   Note: Creates 2 separate batch jobs (outputStager and gcp) and saves them outside the sourceDir.
   Example: `python3 fretransfer.py -expName test_experiment -fileType history -sourceDir $PWD/tests/test_data/history/ -gfdlDir /path/to/GFDL/destination/ -combine -transfer -saveBatchOpts output=/path/for/combine/job/file/stdout account=gfdl_YOURGROUPLETTER job-name=tar_combine_job mail-type=fail -xferBatchOpts output=/path/for/transfer/job/file/stdout account=gfdl_YOURGROUPLETTER job-name=transfer_job mail-type=fail -submit`
   
   * Scenario 3: Combine, no tar, no transfer
   Example: `python3 fretransfer.py -expName test_experiment -fileType history -sourceDir $PWD/tests/test_data/history/ -gfdlDir /path/to/GFDL/destination/ -combine -saveBatchOpts output=/path/for/combine/job/file/stdout account=gfdl_YOURGROUPLETTER job-name=tar_combine_job mail-type=fail -submit`
   
   * Scenario 4: No combine, tar, transfer
   Example: `python3 fretransfer.py -expName test_experiment -fileType history -sourceDir $PWD/tests/test_data/history/ -gfdlDir /path/to/GFDL/destination/ -tar -compress -transfer -saveBatchOpts output=/path/for/tar/job/file/stdout account=gfdl_YOURGROUPLETTER job-name=tar_combine_job mail-type=fail -xferBatchOpts output=/path/for/transfer/job/file/stdout account=gfdl_YOURGROUPLETTER job-name=transfer_job mail-type=fail -submit`
   
   * Scenario 5: No combine, no tar, transfer
   Note: If a .tar file exists outside the sourceDir, fretransfer will natively call output.stager. If not (i.e. only combined files present, mixture of uncombined/combined, and desiring to transfer a directory of all uncombined files), fretransfer will create a gcp batch job and submit it.
   Example: `python3 fretransfer.py -expName test_experiment -fileType history -sourceDir $PWD/tests/test_data/history/ -gfdlDir /path/to/GFDL/destination/ -transfer -xferBatchOpts output=/path/for/transfer/job/file/stdout account=gfdl_YOURGROUPLETTER job-name=transfer_job mail-type=fail -submit`
   
   * Scenario 6: No combine, no tar, no transfer (dry run)
   Example: `python3 fretransfer.py -expName test_experiment -fileType history -sourceDir $PWD/tests/test_data/history/ -gfdlDir /path/to/GFDL/destination/`
   
   * Scenario 7: Combine, tar, no transfer
   Example: `python3 fretransfer.py -expName test_experiment -fileType history -sourceDir $PWD/tests/test_data/history/ -gfdlDir /path/to/GFDL/destination/ -combine -tar -compress -saveBatchOpts account=gfdl_YOURGROUPLETTER job-name=tar_combine_job mail-type=fail -submit`
   
   * Scenario 8: No combine, tar, no transfer
   Example: `python3 fretransfer.py -expName test_experiment -fileType history -sourceDir $PWD/tests/test_data/history/ -gfdlDir /path/to/GFDL/destination/ -tar -saveBatchOpts account=gfdl_YOURGROUPLETTER job-name=tar_combine_job mail-type=fail -submit`

   Note: Only using '-tar' will create an uncompressed archive file. Use '-compress' for the vice versa. 

# Support or Contact
It you are having problems using the code, open an issue in the fretransfer repository:  
https://github.com/NOAA-GFDL/fretransfer/issues

# Disclaimer
The United States Department of Commerce (DOC) GitHub project code is provided on an 'as is' basis and the user assumes responsibility for its use. DOC has relinquished control of the information and no longer has responsibility to protect the integrity, confidentiality, or availability of the information. Any claims against the Department of Commerce stemming from the use of its GitHub project will be governed by all applicable Federal law. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or favoring by the Department of Commerce. The Department of Commerce seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by DOC or the United States Government.
