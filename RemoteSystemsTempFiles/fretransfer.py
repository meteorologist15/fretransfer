#!/usr/bin/python3
# FRETRANSFER
# this is the main fretransfer script
# example: python3 fretransfer -expName mom6_solo_global_ALE_z -fileType history  
# -sourceDir /home/sourceDirectory -destDir /archive/Firstname.Lastname -destMach gfdl
###########################################################################################
import argparse
import fnmatch
import glob
import sys
import os
import re
import subprocess
import shutil
import datetime

# Class for managing  argFile templates
class argFileTemplate:
    
    def __init__(self, fileType):
        self.fileType=fileType
        self.templateName = self.fileType + 'ArgfileTemplate.txt'
#        self.templateLocation = argFileTemplate.get_template(os.path.join(get_fre_dir(),self.templateName))
        self.templateLocation = argFileTemplate.get_template(os.path.join('/home/Jessica.Liptak/fretransfer/RemoteSystemsTempFiles',self.templateName))
        
    @staticmethod
    def get_template(filePath):
        try:
             os.path.isfile(filePath)
        except FileExistsError:
            print("Template file not found")
        
        return filePath
    
    
# Class for argFile to create with a template   
class argFile(argFileTemplate):
 
    def __init__(self, fileType, newFilePath,*args):
       filePatterns = []
       argFileTemplate.__init__(self,fileType)
       # get the full path of new argFile 
       self.newFileLocation = argFile.new_file(self,newFilePath)
       # clean out argFiles from the working directory
       clean_dir(os.path.split(self.newFileLocation)[0],['*.args'])
     
       # get list of files to process
       argFile.get_file_list(self,self.fileType,filePatterns)
     
       # copy the argFile template to the new file
       copy_file(self.templateLocation,self.newFileLocation)
    
    # each new file has a rootFilePath set to None by default    
    # the new file is placed in {newFilePath}/{fileType}
    @staticmethod
    def new_file(self,rootFilePath):
        fileName = argFile.get_new_file_name(self)
        return os.path.join(rootFilePath, self.fileType, fileName)
    
    @staticmethod
    def get_new_file_name(self):
        fileNameRoot = 'output.stager.'
        if self.fileType == 'ascii':
           beginDate = get_time_stamp('-b')
           fileNameAppendix = beginDate + '.A.args'
        elif self.fileType == 'restart':
           endDate = get_time_stamp('-e')
           fileNameAppendix = endDate + '.R.args'
        elif self.fileType == 'history':
            beginDate = get_time_stamp('-b')
            fileNameAppendix = beginDate + '.H.args'           
        newFileName=fileNameRoot + fileNameAppendix
        return newFileName
    
    @staticmethod
    def get_file_list(self,fileType,filePatterns):
        if any(filePatterns):
           patternMatch = filePatterns
        elif fileType == 'ascii': 
           patternMatch = ['*out','*results*','*log*','*timestats*','*stats*','*velocity_truncations*']
        elif fileType == 'restart':
            patternMatch = ['*res*','*nc*','*.input.*tgz','*.ww3']
        elif fileType == 'history':
            patternMatch = ['*nc*','*.ww3']
        
        names=os.listdir('.')
        self.fileList = multi_filter(names, patternMatch)

#Generator function which yields a list of names that match one or more of the patterns."""       
def multi_filter(names, patterns):
    fileList = []
    for name in names:
        for pattern in patterns:
            if fnmatch.fnmatch(name, pattern) and name not in fileList:
                fileList.append(name)
    return fileList
                
# delete file(s) in a directory
def clean_dir(pathName,removeFilePatterns):
    os.chdir(pathName)
    for pattern in removeFilePatterns:
        fileList=glob.glob(pattern)
        for file in fileList:
            os.remove(file)
    
               
def copy_file(srcPath,destPath):
    pathParts = os.path.split(destPath)
    #print(pathParts[0])
    if not os.path.isdir(pathParts[0]):
       os.makedirs(pathParts[0])
       shutil.copy(srcPath,destPath)
    try:
        os.path.isfile(destPath)
    except FileExistsError:
        print("Error: file",destPath ,"not created")
    
def pexec(arg,*args):
    argList = []
    argList.append(arg)
 
    for a in args:
        argList.append(''.join(a)) 
    #print(argList)
    return subprocess.Popen(argList, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# determine the location of the host machine
def get_host_name():
    hostName=os.environ['HOST']
    #print("Host name is", hostName)
    if  any([re.search(r, hostName) for r in ['gfdl.noaa.gov','gaea', 'theia']]):
        return hostName
    else:
        sys.exit('Error: $HOST is not gfdl, gaea, or theia. Exiting.')
# determine the location of the Fre source code and corresponding argFile templates
# assumes that argFile templates will be placed in the fre-commands directory on the host machine
def get_fre_dir():
    hostName=get_host_name()
    freVersion=get_fre_version()
    if 'gfdl.noaa.gov' in hostName:
        freDir = '/home/fms/local/opt/fre-commands/' + freVersion + '/site/gfdl-ws'
    elif 'gaea' in hostName:
        freDir = '/ncrc/home2/fms/local/opt/fre-commands/'  + freVersion + '/site/ncrc_common'
    elif 'theia' in hostName:
        freDir = '/home/fms/local/opt/fre-commands/' + freVersion +  '/site/theia' 
        
    return freDir

# return the fre module file version currently loaded in the environment
def get_fre_version():
    moduleVersion=os.environ['MODULE_VERSION']
   
    moduleCmd='/usr/local/Modules/' + moduleVersion + '/bin/modulecmd'
    #print(moduleCmd)
    p=pexec(moduleCmd,"tcsh", "list")
    # Read stdout and print each new line
    sys.stdout.flush()
    for line in iter(p.stdout.readline, b''):
        sys.stdout.flush()
        # convert the byte object to a string
        lineStr = line.decode()
        # search for the fre version
        if 'bronx-' in lineStr:
           useline = lineStr.strip()
           searchResult=re.search(r'(?<=fre/)\S*',lineStr)
           freVersion = searchResult.group(0)
           #print('Using fre/' + freVersion.strip())
           break
    
    return freVersion
# get the version of hsm
def get_hsm_version():
    cmd = 'which find_module_info'
    p = pexec(cmd,'hsm')
    # Read stdout and print each new line
    sys.stdout.flush()
    for line in iter(p.stdout.readline, b''):
        sys.stdout.flush()
        # convert the byte object to a string
        lineStr = line.decode()
        # search for the fre version
    
def get_time_stamp(*args):
    #print(args)
    baseDir= get_fre_dir()
    
    cmd = os.path.join(baseDir.split("/site")[0],'sbin','time_stamp.csh')
    try:
        os.path.isfile(cmd)
    except FileExistsError:
        print("time_stamp.csh not found in the fre root directory")
        
    #print('time stamp script is ',cmd)
   
    p = pexec(cmd,args)
    
     # Read stdout and print each new line
    sys.stdout.flush()
    for line in iter(p.stdout.readline, b''):
        sys.stdout.flush()
        # convert the byte object to a string
        lineStr = line.decode()
        #print(lineStr)
         # return a string appendixx `tmp(DOY)(HHMMSS)`
        if 'no_time_stamp' in lineStr:
           wereAtNowNow=datetime.datetime.now()
           dateStr = wereAtNowNow.strftime("%Y.%m.%d")
           dt = datetime.datetime.strptime(dateStr, "%Y.%m.%d")
           tt = dt.timetuple()
          
           dateStr = "tmp" +  str(tt.tm_yday) + wereAtNowNow.strftime("%H%M%S")
           break
        else:
           dateStr = lineStr.strip()
           break
       
    return dateStr
# Parse the command-line arguments
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-expName',
                        type=str, 
                        default='',
                        required=True,
                        help='name of the experiment')
    parser.add_argument('-fileType', 
                        default=[], 
                        nargs='+', 
                        required=True,
                        help='type(s) of file(s) to transfer [ascii, history, restart]')
    parser.add_argument('-sourceDir',
                        type=str, 
                        default='',
                        required=True,
                        help='Working directory with ASCII, RESTART, and/or HISTORY sub-directories that contain the \
                        ascii, history, and restart files')
    parser.add_argument('-destDir',
                        type=str,
                        default='',
                        required=True,
                        help='root directory on the destination machine. Files will be transferred to: \
                        ${destDir}/${expName}/[ASCII,RESTART,HISTORY]')
    parser.add_argument('-destMachine', 
                        type=str, 
                        choices=['gaea', 'gfdl', 'theia'],
                        required=True,
                        help='name of the machine to transfer the files to. [gaea, gfdl, theia]')
    # optional user-defined arguments
    parser.add_argument('-makeTarfile', 
                        type=bool,
                        action='store',
                        default=False,
                        help='create a tarball containing the files before transferring? Default = false')
    
    parser.add_argument('-asciiPatterns', default=['out','results', 'log', 'timestats', 'stats'],
                        nargs='?',
                        action='store',
                        help='space-separated list of ascii file patterns to search for.\
                        User-specified pattern(s) replace the default list\
                        Ascii files containing the following patterns are transferred by default:\
                         "out","results", "log", "timestats", "stats", "velocity truncations" ')
    parser.add_argument('-restartPatterns', default=['.res.','.nc.', '.input.', '.tgz$', '.ww3$'],
                        nargs='?',
                        action='store',
                        help='space-separated list of restart file patterns to search for. \
                        User-specified pattern(s) replace the default list. \
                        Restart files containing the following patterns are transferred by default:\
                         ".res.",".nc.", ".input.", ".tgz$", ".ww3$" ')
    parser.add_argument('-historyPatterns', default=['.nc.','.ww3$', '^rregion'],
                        nargs='?',
                        action='store',
                        help='space-separated list of history file patterns to search for.\
                        User-specified pattern(s) replace the default list. \
                        History files containing the following patterns are transferred by default,\
                         "^rregion",".nc.",".ww3$" ')
    parser.add_argument('-stagingType',
                        choices=['chained','online'],
                        action='store',
                        default='chained',
                        nargs='?',
                        help='output staging type. Default is "chained".')
    
 
    # sub-parser for shell variables set by frerun
    subparsers = parser.add_subparsers()

    parser_frerun = subparsers.add_parser('freDefs', help='shell variable definitions set by `frerun`.')
    #parser_frerun.add_argument('-mpiFail',
    #                           action='store_true',
    #                           help='Flag indicating whether the batch job failed ($?MPI_FAIL=1')
    parser_frerun.add_argument('-saveOptions', 
                               action='store',
                               type = str,
                               nargs = '?',
                               required = False,
                               help='options for saving output files to pass to output.stager')
    parser_frerun.add_argument('-xferOptions', 
                               action='store',
                               type = str,
                               nargs = '?',
                               required = False,
                               help='options for transferring output files to pass to output.stager')
    parser_frerun.add_argument('-paramPtmpOn', 
                               action='store',
                               default=0,
                               type = int,
                               choices=[0,1],
                               required = False,
                               help='Flag to copy data to ptmp directory')
    parser_frerun.add_argument('-paramArchiveOn', 
                               action='store',
                               default=0,
                               type = int,
                               choices=[0,1],
                               required = False,
                               help='Flag to move data to archive directory')
    parser_frerun.add_argument('-paramCheckSumOn', 
                               action='store',
                               default=0,
                               type = int,
                               choices=[0,1],
                               required = False,
                               help='Flag to do data checksums')
    parser_frerun.add_argument('-ppStartOn', 
                               action='store',
                               default=0,
                               type = int,
                               choices=[0,1],
                               required = False,
                               help='Flag to start post-processing')
    parser_frerun.add_argument('-paramVerbosityOn', 
                               action='store',
                               default=0,
                               type = int,
                               choices=[0,1],
                               required = False,
                               help='Flag for verbose output')
    parser_frerun.add_argument('-actionCheckOn', 
                               action='store',
                               default=0,
                               type = int,
                               choices=[0,1],
                               required = False,
                               help='Flag to check argfile processing')
    parser_frerun.add_argument('-actionRetryOn', 
                               action='store',
                               default=0,
                               type = int,
                               choices=[0,1],
                               required = False,
                               help='Flag to retry failed transfer jobs')
    parser_frerun.add_argument('-actionSaveOn', 
                               action='store',
                               default=0,
                               type = int,
                               choices=[0,1],
                               required = False,
                               help='Flag to save data')
    parser_frerun.add_argument('-actionXferOn', 
                               action='store',
                               default=0,
                               type = int,
                               choices=[0,1],
                               required = False,
                               help='Flag to transfer data')
    parser_frerun.add_argument('-actionFillGridOn', 
                               action='store',
                               default=0,
                               type = int,
                               choices=[0,1],
                               required = False,
                               help='Flag to perform grid filling')
    parser_frerun.add_argument('-saveRetries', 
                               action='store',
                               default=0,
                               type = int,
                               required = False,
                               help='Number of times to retry failed save jobs')
    parser_frerun.add_argument('-xferRetries', 
                               action='store',
                               default=0,
                               type = int,
                               required = False,
                               help='Number of times to retry failed transfer jobs')
    parser_frerun.add_argument('-saveRetry', 
                               action='store',
                               default=0,
                               type = int,
                               choices=[0,1],
                               required = False,
                               help='Flag to retry failed save jobs')
    parser_frerun.add_argument('-xferRetry', 
                               action='store',
                               default=0,
                               type = int,
                               choices=[0,1],
                               required = False,
                               help='Flag to retry failed transfer jobs')
    
    args = parser.parse_args()

    return args
    

# main program
def main():
  # parse the arguments
  args = parse_args()
  #for arg in vars(args):
  #   print(arg, getattr(args, arg))
  print(args.saveOptions)
  # set up files
  for ftype in args.fileType:
        assert (ftype == 'ascii' or ftype == 'restart' or ftype == 'history'), 'Invalid fileType value.,\
                Must be `history`, `ascii`, or `restart`'
        sourcePath = os.path.join(args.sourceDir,ftype)
        assert (os.path.exists(sourcePath)), 'Error: directory does not exist.'
                
        os.chdir(sourcePath)
        
        A=argFile(ftype,'/home/Jessica.Liptak/temp')
       
               
        
       
#      f = open(argFile,'a')
        
#      f.close

main()
