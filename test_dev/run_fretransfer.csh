#!/bin/csh -fx

#module load fre/bronx-16

#python3 fretransfer.py userDefs -expName test_fretransfer -fileType restart history ascii \
 #-sourceDir ${PWD}/test_dev -destDir /archive/${USER} -destMach gfdl \
 #-groupAccount gfdl_f

set workDir=/lustre/f2/scratch/Jessica.Liptak/work/master_mom6_2019.11.27_dev_gfdl/mom6_solo_global_ALE_z_1x0m2d_36pe.o268566271
set tmpOutputDir=${workDir}/output.stager

pushd $workDir

# copy the ascii output to output.stager directory
if ( -e $workDir ) then
   if ( -d $workDir ) then
      if ( -r $workDir ) then
         if ( -w $workDir ) then
            ls -1 --directory --file-type $workDir/* | grep --fixed-strings --invert-match $tmpOutputDir | xargs rm --force --recursive
         endif
      endif
   endif
endif
# copy the restart output
set patternGrepRestart='\<res\>|\<nc\>|\.input.\tgz$|\.ww3$'
set restartWorkDir=$tmpOutputDir/RESTART
if (! -d ${restartWorkDir} ) then
  mkdir -p ${restartWorkDir}
endif

cd RESTART
ls -1 | egrep "${patternGrepRestart}" | xargs ln --force --target-directory=${restartWorkDir}
 

python3 fretransfer.py userDefs -expName test_fretransfer -fileType restart \
-sourceDir ${workDir} -destDir /archive/${USER} -destMach gfdl -groupAccount gfdl_f
