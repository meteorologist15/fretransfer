#!/usr/bin/python3
# FRETRANSFER
# this is the main fretransfer script
# example: python3 fretransfer -expName mom6_solo_global_ALE_z -fileType history  
# -sourceDir /home/sourceDirectory -destDir /archive/Firstname.Lastname -destMach gfdl
###########################################################################################
import argparse
import fnmatch
import logging
import glob
import sys
import os
import re
import subprocess
import shutil
import datetime


logging_format = logging_format = '%(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=logging_format)


# Class for managing  argFile templates
class argFileTemplate:
    
    def __init__(self, fileType):
        self.fileType=fileType
        self.templateName = self.fileType + 'ArgfileTemplate.txt'
        self.templateLocation = argFileTemplate.get_template(os.path.join('/home/Jessica.Liptak/fretransfer/RemoteSystemsTempFiles',self.templateName))
        
    @staticmethod
    def get_template(filePath):
        try:
             os.path.isfile(filePath)
        except FileNotFoundError:
            logging.info("Template file not found")
        
        return filePath
    
# Class for argFile to create with a template   
class argFile(argFileTemplate):
 
    def __init__(self, fileType, newFilePath,*args):
       filePatterns = []
       argFileTemplate.__init__(self,fileType)
       # get the full path of new argFile 
       self.newFileLocation = argFile.new_file(self,newFilePath)
       
     
       # get list of files to process
       argFile.get_file_list(self,self.fileType,filePatterns)
     
    
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

# write the data to the file
def write_file(filePath,fileStatus="",**kwargs):
    try:
        fileStatus == "w" or fileStatus == "a"
    except ValueError:
        logging.info("Error: fileStatus must be `w` or `a`")
           
    shutil.copy(filePath, filePath+"~" )
    # read in lines from the temporary sourceFile
    source= open(filePath+"~", "r" )
    lines = []
    for line in source:
        #print(line)
        lines.append(line)
    source.close()
    # replace lines with values if they exist
    for key, value in kwargs.items():
        logging.info(key, str(value))
        for index,line in enumerate(lines):
            if key in line:
                if 'setenv'in line:
                    lines[index] = 'setenv ' + key + '' + str(value)
                else:
                    lines[index] = 'set ' + key + ' = ' + str(value)
                break
              
    # write values to argFile
    destination = open(filePath, fileStatus)
    for line in lines:
        if len(line.strip()) > 0:
            destination.write(line + '\n')       
    
    destination.close()
    # remove the temporary file
    filePathParts = os.path.split(filePath)
    clean_dir(filePathParts[0],[filePathParts[1]+'~'])

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
    if not os.path.isdir(pathParts[0]):
        os.makedirs(pathParts[0])
        
    shutil.copyfile(srcPath,destPath)
    try:
        os.path.isfile(destPath)
    except FileNotFoundError:
        logging.info("Error: file",destPath ,"not created")
    
def pexec(arg,*args):
    argList = []
    argList.append(arg)
 
    for a in args:
        argList.append(''.join(a)) 
    return subprocess.Popen(argList, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# determine the location of the host machine
def get_host_name():
    hostName=os.environ['HOST']
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
# create a time stamp to append to the temporary argFiles and directory.
def get_time_stamp(*args):
    #print(args)
    baseDir= get_fre_dir()
    
    cmd = os.path.join(baseDir.split("/site")[0],'sbin','time_stamp.csh')
    try:
        os.path.isfile(cmd)
    except FileNotFoundError:
        logging.info("time_stamp.csh not found in the fre root directory")
    p = pexec(cmd,args)
    
     # Read stdout and print each new line
    sys.stdout.flush()
    for line in iter(p.stdout.readline, b''):
        sys.stdout.flush()
        # convert the byte object to a string
        lineStr = line.decode()
         # return a string appendix `tmp(DOY)(HHMMSS)`
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
    parser.add_argument("-help", help='Generate an argFile with user-defined parameters and fre-defined \
                                     shell variables. Example with user-defined arguments: python3 fretransfer.py userDefs \
                                     -expName myExperiment -fileType history restart ascii -sourceDir /home/Jessica.Liptak/temp \
                                     -destDir /archive/Firstname.Lastname -destMachine gfdl \
                                     Example with fre-defined shell variables: python3 fretransfer.py freDefs -paramCheckSumOn 1 ' )
    subparsers = parser.add_subparsers(dest='defCategory')
    
    # sub-parser for user-defined options
    parser_userDef = subparsers.add_parser('userDefs', help='User-defined options')
    parser_userDef.add_argument('-expName',
                        type=str, 
                        default='',
                        required=True,
                        help='name of the experiment')
    parser_userDef.add_argument('-fileType', 
                        default=[], 
                        nargs='+', 
                        required=True,
                        help='type(s) of file(s) to transfer [ascii, history, restart]')
    parser_userDef.add_argument('-sourceDir',
                        type=str, 
                        default='',
                        required=True,
                        dest = 'workDir',
                        help='Working directory with ASCII, RESTART, and/or HISTORY sub-directories that contain the \
                        ascii, history, and restart files generated during a model simulation.')
    parser_userDef.add_argument('-destDir',
                        type=str,
                        default='',
                        required=True,
                        dest = 'outputDirRemote',
                        help='root directory on the destination machine. Files will be transferred to: \
                        ${destDir}/${expName}/[ASCII,RESTART,HISTORY]')
    parser_userDef.add_argument('-destMachine', 
                        type=str, 
                        choices=['gaea', 'gfdl', 'theia'],
                        required=True,
                        help='name of the machine to transfer the files to. [gaea, gfdl, theia]')
    # optional user-defined arguments
    parser_userDef.add_argument('-makeTarfile', 
                        type=int,
                        action='store',
                        default=0,
                        choices=[0,1],
                        dest='paramCompressOn',
                        help='create a tarball containing the files before transferring? Default = false')
    
    parser_userDef.add_argument('-asciiPatterns', default=['out','results', 'log', 'timestats', 'stats'],
                        nargs='?',
                        action='store',
                        help='space-separated list of ascii file patterns to search for.\
                        User-specified pattern(s) replace the default list\
                        Ascii files containing the following patterns are transferred by default:\
                         "out","results", "log", "timestats", "stats", "velocity truncations" ')
    parser_userDef.add_argument('-restartPatterns', default=['.res.','.nc.', '.input.', '.tgz$', '.ww3$'],
                        nargs='?',
                        action='store',
                        help='space-separated list of restart file patterns to search for. \
                        User-specified pattern(s) replace the default list. \
                        Restart files containing the following patterns are transferred by default:\
                         ".res.",".nc.", ".input.", ".tgz$", ".ww3$" ')
    parser_userDef.add_argument('-historyPatterns', default=['.nc.','.ww3$', '^rregion'],
                        nargs='?',
                        action='store',
                        help='space-separated list of history file patterns to search for.\
                        User-specified pattern(s) replace the default list. \
                        History files containing the following patterns are transferred by default,\
                         "^rregion",".nc.",".ww3$" ')
    parser_userDef.add_argument('-stagingType',
                        choices=['chained','online'],
                        action='store',
                        default='chained',
                        help='output staging type. Default is "chained".')
    
 
    # sub-parser for shell variables set by frerun

    parser_frerun = subparsers.add_parser('freDefs', help='Shell variables set by `frerun`.')
    parser_frerun.add_argument('-fileType', 
                        default=[], 
                        nargs='+', 
                        required=True,
                        help='type(s) of file(s) to transfer [ascii, history, restart]')
    parser_frerun.add_argument('-sourceDir',
                        type=str, 
                        default='',
                        required=True,
                        dest = 'workDir',
                        help='Working directory with ASCII, RESTART, and/or HISTORY sub-directories that contain the \
                        ascii, history, and restart files generated during a model simulation.')
    parser_frerun.add_argument('-archDir', 
                               action='store',
                               default = '',
                               type = str,
                               required = False,
                               help='Archive directory')
    parser_frerun.add_argument('-ptmpDir', 
                               action='store',
                               default = '',
                               type = str,
                               required = False,
                               help='Ptmp directory to copy output to.')
    parser_frerun.add_argument('-includeDir', 
                               action='store',
                               default = '',
                               type = str,
                               required = False,
                               help='Directory with files to include')
    parser_frerun.add_argument('-includeDirRemote', 
                               action='store',
                               default = '',
                               type = str,
                               required = False,
                               help='Remote directory with files to include')
    
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
    parser_frerun.add_argument('-ppStarterOptions', 
                               action='store',
                               type = str,
                               nargs = '?',
                               required = False,
                               help='list of post processing options')
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
    parser_frerun.add_argument('-actionCombineOn', 
                               action='store',
                               default=0,
                               type = int,
                               choices=[0,1],
                               required = False,
                               help='Flag to check combine uncombined files')
    parser_frerun.add_argument('-gridSpec', 
                               action='store',
                               default='',
                               type = str,
                               required = False,
                               help='Name of the gridSpec file')
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
    parser_frerun.add_argument('-hsmModuleFilesDir', 
                               action='store',
                               default='',
                               type = str,
                               required = False,
                               help='Path to the hsm module file directory')
    parser_frerun.add_argument('-hsmVersion', 
                               action='store',
                               default='',
                               type = str,
                               required = False,
                               help='Version of hsm currently loaded in the environment')
    parser_frerun.add_argument('-modulesHomeDir', 
                               action='store',
                               default='',
                               type = str,
                               required = False,
                               help='Path to module file home directory')
    parser_frerun.add_argument('-xferToolModuleFilesDir', 
                               action='store',
                               default='',
                               type = str,
                               required = False,
                               help='Path to the fre transfer tools module file directory')
    parser_frerun.add_argument('-xferToolVersion', 
                               action='store',
                               default='',
                               type = str,
                               required = False,
                               help='Version of the fre transfer tools currently loaded in the environment')
    parser_frerun.add_argument('-mppnccombineOptString', 
                               action='store',
                               default='',
                               type = str,
                               required = False,
                               help='options to pass to mppnccombine')
    parser_frerun.add_argument('-xmlFiles', 
                               action='store',
                               default='',
                               type = str,
                               required = False,
                               help='xml file(s) used for model simulation')
    parser_frerun.add_argument('-xmlFilesRemote', 
                               action='store',
                               default='',
                               type = str,
                               required = False,
                               help='remote xml files for post-processing')
    parser_frerun.add_argument('-FRE_HSM_TEST_VERSION', 
                               action='store',
                               default='',
                               type = str,
                               required = False,
                               help='Version of HSM currently loaded in the environment if fre version is TEST')
    
    parser_frerun.add_argument('-FRE_GCP_TEST_VERSION', 
                               action='store',
                               default='',
                               type = str,
                               required = False,
                               help='Version of GCP currently loaded in the environment if fre version is TEST')
    parser_frerun.add_argument('-FRE_COMMANDS_TEST', 
                               action='store',
                               default='',
                               type = str,
                               required = False,
                               help = 'Version of fre commands currently loaded in the environment if fre version is\
                                    test')
    parser_frerun.add_argument('-FRE_NCTOOLS_TEST', 
                               action='store',
                               default='',
                               type = str,
                               required = False,
                               help ='Version of fre nctools currently loaded in the environment if fre version is \
                                     TEST')
    parser_frerun.add_argument('-FRE_CURATOR_TEST', 
                               action='store',
                               default='',
                               type = str,
                               required = False,
                               help='Version of fre curator currently loaded in the environment if fre version is TEST')
    args = parser.parse_args()

    return args
    

# main program
def main():
  # parse the arguments
  args = parse_args()
  # set up argFiles with user-defined options
  
  if args.defCategory == 'userDefs':
    logging.info('Parsing Userdefs')
    
    # make a dictionary
    argDict = {}
    for a in vars(args):
        argDict[a] = getattr(args,a)
    
    for ftype in args.fileType:
        try: 
            ftype == 'ascii' or ftype == 'restart' or ftype == 'history'
        except ValueError:
            logging.info('Invalid fileType value. Must be `history`, `ascii`, or `restart`')
                
        sourcePath = os.path.join(args.workDir,ftype)
        try:
            os.path.exists(sourcePath)
        except NotADirectoryError:
            logging.info('Error: directory',sourcePath,'does not exist.')
                
        os.chdir(sourcePath)
      
        A=argFile(ftype,'/home/Jessica.Liptak/temp')
        
        # clean out argFiles from the working directory
        clean_dir(os.path.split(A.newFileLocation)[0],['*.args*'])
        # copy the template file to the working directory
        copy_file(A.templateLocation,A.newFileLocation)
        # write values in the argDict to the argFile
        write_file(A.newFileLocation,"w",**argDict)
        
  elif args.defCategory == 'freDefs':
    logging.info('Parsing freDefs')
     # make a dictionary
    argDict = {}
    for a in vars(args):
        if a != 'fileType' and a != 'workDir':
            argDict[a] = getattr(args,a)
    for ftype in args.fileType:
        try: 
            ftype == 'ascii' or ftype == 'restart' or ftype == 'history'
        except ValueError:
            logging.error('Invalid fileType value. Must be `history`, `ascii`, or `restart`')
                
        sourcePath = os.path.join(args.workDir,ftype)
        try:
            os.path.exists(sourcePath)
        except NotADirectoryError:
            logging.error('Error: directory',sourcePath,'does not exist.')
        
        os.chdir(sourcePath)
        # check that one argFile already exists in the working directory 
        argFiles = [n for n in glob.glob('*.args') if os.path.isfile(n)]
        try:
            any(argFiles[0].strip())
        except FileNotFoundError:
            logging.error('Error: no',fType,'argFile found in',sourcePath)
        try:
            len(argFiles) == 1
        except FileExistsError:
            logging.error('Error: multiple',fType,'argFiles found in ',sourcePath)
        # write the fre definitions to the existing argFile
        filePath = os.path.join(sourcePath,argFiles[0])
        write_file(filePath,"w",**argDict)
            
        
if __name__ == '__main__': 

    main()

