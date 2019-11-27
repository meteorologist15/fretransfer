#!/bin/csh -fx

#module load fre/bronx-16

python3 fretransfer.py userDefs -expName test_fretransfer -fileType restart history ascii \
 -sourceDir ${PWD}/test_dev -destDir /archive/${USER} -destMach gfdl \
 -groupAccount gfdl_f
