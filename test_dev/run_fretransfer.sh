#!/bin/sh

#module load fre/bronx-16

#python3 fretransfer.py userDefs -expName test_fretransfer -fileType restart history ascii \
 #-sourceDir ${PWD}/test_dev -destDir /archive/${USER} -destMach gfdl \
 #-groupAccount gfdl_f

workDir=/lustre/f2/scratch/${USER}/work/master_mom6_2019.11.27_dev_gfdl/mom6_solo_global_ALE_z_1x0m2d_36pe.o268566271
tmpOutputDir=${workDir}/output.stager

pushd $workDir

# copy the restart output
patternGrepRestart='\<res\>|\<nc\>|\.input.\tgz$|\.ww3$'
restartWorkDir=${tmpOutputDir}/RESTART

if [ ! -d ${restartWorkDir} ] ; then
  mkdir -p ${restartWorkDir}
fi

cd RESTART
ls -1 | egrep "${patternGrepRestart}" | xargs ln --force --target-directory=${restartWorkDir}
 

python3 fretransfer.py userDefs -expName test_fretransfer -fileType restart \
-sourceDir ${workDir} -destDir /archive/${USER} -destMach gfdl -groupAccount gfdl_f
