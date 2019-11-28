#!/bin/sh

#module load fre/bronx-16

#python3 fretransfer.py userDefs -expName test_fretransfer -fileType restart history ascii \
 #-sourceDir ${PWD}/test_dev -destDir /archive/${USER} -destMach gfdl \
 #-groupAccount gfdl_f

cwd=${PWD}

alias fretransfer='python3 ${HOME}/fretransfer/fretransfer.py'

workDir=/lustre/f2/scratch/${USER}/work/master_mom6_2019.11.28_dev_gfdl/mom6_solo_global_ALE_z_1x0m1d_36pe.o268566607
tmpOutputDir=/lustre/f2/scratch/${USER}/tmp/test_fretransfer/output.stager

pushd $workDir

# copy the restart output
patternGrepRestart='\<res\>|\<nc\>|\.input.\tgz$|\.ww3$'
restartWorkDir=${tmpOutputDir}/RESTART

if [ ! -d ${restartWorkDir} ] ; then
  mkdir -p ${restartWorkDir}
fi

cd RESTART
ls -1 | egrep "${patternGrepRestart}" | xargs ln --force --target-directory=${restartWorkDir}

popd
cd ${cwd}

fretransfer userDefs -expName test_fretransfer -fileType restart \
-sourceDir ${tmpOutputDir} -destDir /archive/${USER} -destMach gfdl -groupAccount gfdl_f
