#!/bin/csh -fx
#FRE scheduler-options
#SBATCH --chdir=/lustre/f2/dev/Jessica.Liptak/MOM6_solo_liptak_fork_dev_gfdl/xanadu_mom6_2019.06.20_dev_gfdl/mom6_solo_global_ALE_z/ncrc3.gnu7-debug/stdout/run
#SBATCH --output=/lustre/f2/dev/Jessica.Liptak/MOM6_solo_liptak_fork_dev_gfdl/xanadu_mom6_2019.06.20_dev_gfdl/mom6_solo_global_ALE_z/ncrc3.gnu7-debug/stdout/run/%x.o%j
#SBATCH --job-name=mom6_solo_global_ALE_z_1x0m5d_36pe
#SBATCH --comment=bronx-15
#SBATCH --time=10
#SBATCH --qos=normal
#SBATCH --partition=batch
#SBATCH --mail-type=fail
#SBATCH --export=NONE
#SBATCH --clusters=c3
#SBATCH --nodes=2
#SBATCH --account=gfdl_f

# interactive session salloc --account=gfdl_f --nodes=2 --ntasks=36 --clusters=c3 --time=2:00:00

#===============================================================================
# The script created at 2019-06-21T16:20:24 via:
# /ncrc/home2/fms/local/opt/fre-commands/bronx-15/bin/frerun --archive --cluster=c3 --combine-history --ncores=1 --overwrite --platform=ncrc3.gnu7 --qos=normal --regression=basic --target=debug --walltime=240 --xmlfile=/lustre/f2/dev/gfdl/Jessica.Liptak/xml/MOM6_solo.xml mom6_solo_global_ALE_z
#===============================================================================

set modulesHomeDir=/opt/modules/default
source $modulesHomeDir/init/tcsh

module use /sw/gaea/modulefiles

module use -a /usw/eslogin/modulefiles-c4

module load CmrsEnv

module load banner
setenv COLUMNS 148
if ( $echoOn ) set echo

set FRE_JOBID='test'
banner $FRE_JOBID

################################################################################
#---------------- global constants and variables, set by frerun ----------------
################################################################################

set freCommandsModuleFilesDir=/ncrc/home2/fms/local/modulefiles
set freCommandsVersion=bronx-15

set project=gfdl_f

set platform=ncrc3.gnu7
set target=debug
set name=mom6_solo_global_ALE_z
set rtsxml=/lustre/f2/dev/gfdl/Jessica.Liptak/xml/MOM6_solo.xml
set stdoutDir=/lustre/f2/dev/Jessica.Liptak/MOM6_solo_liptak_fork_dev_gfdl/xanadu_mom6_2019.06.20_dev_gfdl/mom6_solo_global_ALE_z/ncrc3.gnu7-debug/stdout/run
set stdoutTmpDir=/lustre/f2/dev/Jessica.Liptak/MOM6_solo_liptak_fork_dev_gfdl/xanadu_mom6_2019.06.20_dev_gfdl/mom6_solo_global_ALE_z/ncrc3.gnu7-debug/stdout/run
set stateDir=/lustre/f2/dev/Jessica.Liptak/MOM6_solo_liptak_fork_dev_gfdl/xanadu_mom6_2019.06.20_dev_gfdl/mom6_solo_global_ALE_z/ncrc3.gnu7-debug/state/1x0m5d_36pe/run
set workDir=/lustre/f2/scratch/Jessica.Liptak/work/xanadu_mom6_2019.05.24_dev_gfdl/mom6_solo_global_ALE_z_gnu7_debug_gaea.o1561732749/
set ptmpDir=/lustre/f2/scratch/Jessica.Liptak/ptmp
set archiveDir=/lustre/f2/dev/Jessica.Liptak/MOM6_solo_liptak_fork_dev_gfdl/xanadu_mom6_2019.06.20_dev_gfdl/mom6_solo_global_ALE_z/ncrc3.gnu7-debug/archive
set scriptName=/lustre/f2/dev/Jessica.Liptak/MOM6_solo_liptak_fork_dev_gfdl/xanadu_mom6_2019.06.20_dev_gfdl/mom6_solo_global_ALE_z/ncrc3.gnu7-debug/scripts/run/mom6_solo_global_ALE_z_1x0m5d_36pe
set executable=/lustre/f2/dev/Jessica.Liptak/MOM6_solo_liptak_fork_dev_gfdl/mom6_solo_compile/ncrc3.gnu7-debug/exec/fms_mom6_solo_compile.x
set segmentsPerSimulation=1
set segmentsPerPPCall=0
set segmentsPerJob=1
set monthslist=(0)
set dayslist=(5)
set hourslist=(0)
set timeStampOptions=(-f digital)
set baseDate='0 0 0 0 0 0'
set mailMode=fail
set includeDir=
set includeDirRemote= 

set platformRemote=''
set stdoutDirRemote=''
set stmpDirRemote=''
set archiveDirRemote=''
set envRemote=''
set freCommandsVersionRemote=''

set outputStagerSaveCluster=es
set outputStagerSavePartition=ldtn
set outputStagerSaveCoreSpec=01
set outputStagerSaveRuntimeAscii=8:00:00
set outputStagerSaveRuntimeRestart=8:00:00
set outputStagerSaveRuntimeHistory=8:00:00
set outputStagerSaveRetries=4

set outputStagerXferCluster=es
set outputStagerXferPartition=rdtn
set outputStagerXferCoreSpec=01
set outputStagerXferRuntimeAscii=16:00:00
set outputStagerXferRuntimeRestart=16:00:00
set outputStagerXferRuntimeHistory=16:00:00
set outputStagerXferRetries=4

set workDirCleanerPartition=ldtn
set workDirCleanerCoreSpec=01
set workDirCleanerRuntime=8:00

set finisherPartition=ldtn
set finisherCoreSpec=01
set finisherRuntime=8:00

set ppStarterCluster=gfdl
set ppStarterPartition=stage
set ppStarterCoreSpec=01
set ppStarterCombineOffLargeOffConstraint= 
set ppStarterCombineOffLargeOffRuntime=12:00:00
set ppStarterCombineOffLargeOnConstraint=bigvftmp
set ppStarterCombineOffLargeOnRuntime=16:00:00
set ppStarterCombineOnLargeOffConstraint= 
set ppStarterCombineOnLargeOffRuntime=1:00:00
set ppStarterCombineOnLargeOnConstraint= 
set ppStarterCombineOnLargeOnRuntime=1:00:00
set ppStarterHistorySizeThreshold=8192

set flagRunTypeRegression
set flagCheckSumOff
set flagWorkDirCleanOff
set flagOutputTypeOverwrite
set flagOutputFormat64Bit
set flagOutputStagingTypeChained
set flagOutputCacheHistoryOff
set flagOutputCombineHistoryOn
set flagOutputCompressAsciiOff
set flagOutputCompressRestartOff
set flagOutputCompressHistoryOff
set flagOutputArchiveOn
set flagOutputPostProcessOff
set flagOutputXferOff
set flagOutputCheckOff
set flagVerbosityOff
set flagOutputFillGridOff

set outputDir=/lustre/f2/dev/Jessica.Liptak/MOM6_solo_liptak_fork_dev_gfdl/xanadu_mom6_2019.06.20_dev_gfdl/mom6_solo_global_ALE_z/ncrc3.gnu7-debug/archive/1x0m5d_36pe
set gridSpec=/lustre/f2/pdata/gfdl/gfdl_O/datasets/global/siena_201204/mosaic.unpacked/grid_spec.nc
set initCond=/lustre/f2/pdata/gfdl/gfdl_O/datasets/global/siena_201204/INPUT/GOLD_IC.2010.11.15.nc

set npes=36
set atm_ranks= 
set tot_atm_ranks= 
set atm_threads= 
set atm_layout= 
set atm_io_layout= 
set atm_mask_table= 
set atm_hyperthread=.false.
set scheduler_atm_threads= 
set ocn_ranks=36
set tot_ocn_ranks= 
set ocn_threads= 
set ocn_layout=9,4
set ocn_io_layout=1,1
set ocn_mask_table=MOM_mask_table
set ocn_hyperthread=.false.
set scheduler_ocn_threads=1
set lnd_ranks= 
set tot_lnd_ranks= 
set lnd_threads= 
set lnd_layout= 
set lnd_io_layout= 
set lnd_mask_table= 
set lnd_hyperthread=.false.
set scheduler_lnd_threads= 
set ice_ranks= 
set tot_ice_ranks= 
set ice_threads= 
set ice_layout=6,6
set ice_io_layout=1,1
set ice_mask_table=MOM_mask_table
set ice_hyperthread=.false.
set scheduler_ice_threads= 

alias runCommand time `which srun` --verbose --export=ALL --ntasks=$npes --cpus-per-task=1 ./$executable:t
alias runCommandTest echo Not using srun-multi

set mppnccombineOptsRestart='-64 -h 16384 -m'
set mppnccombineOptsHistory='-64 -h 16384 -m'

set FreCommandsSrcDir=/lustre/f2/dev/Jessica.Liptak/MOM6_solo_liptak_fork_dev_gfdl/mom6_solo_compile/src
set FreCommandsBldDir=/lustre/f2/dev/Jessica.Liptak/MOM6_solo_liptak_fork_dev_gfdl/mom6_solo_compile/ncrc3.gnu7-debug/exec

################################################################################
#------------------------ global constants and aliases -------------------------
################################################################################

if ( -d $freCommandsModuleFilesDir && -r $freCommandsModuleFilesDir ) then
   module use $freCommandsModuleFilesDir
else
   if ( $echoOn ) unset echo
   echo "*ERROR*: The 'fre' modulefiles directory '$freCommandsModuleFilesDir' doesn't exist or not readable"
   if ( $echoOn ) set echos
endif

if ( $echoOn ) unset echo

# Platform environment defaults from /ncrc/home2/fms/local/opt/fre-commands/bronx-15/site/ncrc3/env.defaults.gnu
module unload cray-netcdf cray-hdf5 fre
module unload PrgEnv-pgi PrgEnv-intel PrgEnv-gnu PrgEnv-cray
module load PrgEnv-gnu/6.0.3
module swap gcc gcc/7.2.0
module load fre/bronx-15
module load cray-hdf5/1.8.16
module load git

setenv KMP_STACKSIZE 512m
setenv NC_BLKSZ 1M
setenv F_UFMTENDIAN big
# MAIN_PROGRAM env is needed by the GNU compiler
setenv MAIN_PROGRAM coupler/coupler_main.o
# Platform environment overrides from XML

module list
if ( $echoOn ) set echo

set freCommandsModuleFile=$freCommandsModuleFilesDir/fre/$freCommandsVersion
if ( -f $freCommandsModuleFile && -r $freCommandsModuleFile ) then
   if ( $echoOn ) unset echo
   module unload fre
   module use $freCommandsModuleFilesDir
   module load fre/$freCommandsVersion
   if ( $echoOn ) set echo
else
   if ( $echoOn ) unset echo
   echo "*ERROR*: The 'fre' modulefile '$freCommandsModuleFile' doesn't exist or not readable"
   if ( $echoOn ) set echo
endif
unset freCommandsModuleFile

set architecture='x86_64'

set machine=`uname -m`

if ( $machine != $architecture ) then
   if ( $echoOn ) unset echo
   echo "*ERROR*: The script '$scriptName' is intended for the machine architecture '$architecture'"
   if ( $echoOn ) set echo
endif

unset machine

set work=$workDir

set hsmDir=$workDir/hsm

set tmpOutputDir=$workDir/output.stager

set checkPointDir=/usw/checkpoint

set envFile=/tmp/shell.variables.$FRE_JOBID
set envFileDelay=2

set patternGrepAscii='\<out\>|\<results\>|\<log\>|\<timestats\>|\<stats\>|\<velocity_truncations\>'
set patternGrepRestart='\<res\>|\<nc\>|\.input.\tgz$|\.ww3$'
set patternGrepRestartNextDrop='\<res\>'
set patternGrepRestartNextMove='\<res\>|\<nc\>|\.ww3$'
set patternGrepHistory='\<nc\>|\.ww3$'
set patternGrepRegion='^rregion'

set patternSedHome='s/^\/(autofs|ncrc)\/.+\/'$USER'\//\/home\/'$USER'\/ncrc\//'
set patternSedSCRATCH='s|^'$SCRATCH'/?([^/]*/)?'$USER'/|/home/'$USER'/ncrc/|'
set patternSedDEV='s|^'$DEV'/?([^/]*/)?'$USER'/|/home/'$USER'/ncrc/|'

set patternSedCTMP="$patternSedSCRATCH"
set patternSedCPERM="$patternSedDEV"

set archExt='tar'

set submitOptionsCommon=(--mail-type=$mailMode)
set submitOptionsOutputStagerSave=($submitOptionsCommon --chdir=$stdoutDir --output=$stdoutDir/%x.o%j --clusters=$outputStagerSaveCluster --partition=$outputStagerSavePartition)
set submitOptionsOutputStagerXfer=($submitOptionsCommon --chdir=$stdoutDir --output=$stdoutDir/%x.o%j --clusters=$outputStagerXferCluster --partition=$outputStagerXferPartition)
set submitOptionsWorkDirCleaner=($submitOptionsCommon --chdir=$stdoutDir --output=$stdoutDir/%x.o%j --partition=$workDirCleanerPartition)
set submitOptionsFinisher=($submitOptionsCommon --chdir=$stdoutDir --output=$stdoutDir/%x.o%j --partition=$finisherPartition)
set submitOptionsPPStarter=($submitOptionsCommon --clusters=$ppStarterCluster --partition=$ppStarterPartition)

set outputStagingType=`set | grep '^flagOutputStagingType' | sed 's/flagOutputStagingType//'`

alias expandVariables `which expand_variables` --verbose
alias findModuleInfo `which find_module_info` --verbose
alias findXIncludes `which find_xincludes` --verbose
alias finisher `which batch_copy.csh`
alias prepareDir `which prepare_dir.csh`
alias timeStamp `which time_stamp.csh` $timeStampOptions
alias workDirCleaner `which batch_rmdir.csh`
alias adjust_dry_mass_tool `which adjust_dry_mass.csh`

set workDirCleaner=`alias workDirCleaner`
set finisher=`alias finisher`

alias submit `which batch.scheduler.submit` --verbose
alias outputStager `which output.stager`

set outputStager=`alias outputStager`
@ outputStagerErrors=0

alias find `which lfs` find


################################################################################
#---------------------------------- finisher -----------------------------------
################################################################################

if ( $?batch && ! $?FRE_STAGE && ( "$stdoutDir" != "$stdoutTmpDir" ) ) then
   set finisherOptions=($submitOptionsFinisher --job-name=test.finisher)
   set finisherOptions=($finisherOptions --time=$finisherRuntime --mincpus=$finisherCoreSpec)
   set finisherOptions=($finisherOptions --export=src=$stdoutTmpDir/test,dstDir=$stdoutDir)
   set finisherOptions=($finisherOptions --dependency=afterany:test)

   set finisherResult=`submit -O "$finisherOptions" $finisher`

   if ( $status == 0 ) then
      if ( $echoOn ) unset echo
      echo "<NOTE> : The finisher job '$finisherResult' has been submitted successfully"
      if ( $echoOn ) set echo
   else
      if ( $echoOn ) unset echo
      echo "WARNING: Can't submit the finisher job"
      if ( $echoOn ) set echo
   endif

   unset finisherResult
   unset finisherOptions
endif

################################################################################
#----------------------------- global variables --------------------------------
################################################################################

set continueFlag=1

set submitOptionsProject=(--account=$project)

set combineList=( )
set saveJobIds=( )
set argFiles=( )

@ currentSeg=1
@ irun=1

if ( $?fyear ) then
   #remove leading zeros, fyear as integer
   set fyearint=`echo $fyear | sed 's/^0*//'`
   if ( ${fyearint} > 0 ) then
      @ fyearm1=${fyearint} - 1
      set fyearm1=`printf "%04d" $fyearm1`
   else
      set fyearm1='0000'
   endif
   @ fyearp1=${fyearint} + 1
   set fyearp1=`printf "%04d" $fyearp1`
   @ fyearp2=${fyearint} + 2
   set fyearp2=`printf "%04d" $fyearp2`
endif

if ( $?ireload ) then
   # Using old way to calculate currentSeg
   # Get best guess --- may not be correct if user changed number of segments
   # per job after job started --- frerun -e does not update state file
   @ currentSeg=( $ireload - 1 )*$segmentsPerJob+$irun
endif

cd $workDir

set dataFilesNotOK=( )

if ( $#dataFilesNotOK > 0 ) then
   if ( $echoOn ) unset echo
   foreach dataFile ( $dataFilesNotOK )
      echo "*ERROR*: A problem with the data file: $dataFile"
   end
   echo "*ERROR*: Failed to copy data files"
   if ( $echoOn ) set echo
endif

set mom6ExpDir=/lustre/f2/dev/Jessica.Liptak/MOM6_solo_liptak_fork/mom6_solo_compile/src/mom6/MOM6-examples/ocean_only/global_ALE/z









