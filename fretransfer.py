#!/usr/bin/python3
# FRETRANSFER
# this is the main fretransfer script
# example: python3 fretransfer userDefs -expName mom6_solo_global_ALE_z -fileType history \
# -sourceDir /home/sourceDirectory -destDir /archive/Firstname.Lastname -destMach gfdl \
# -groupAccount gfdl_f
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
        templateDir = os.path.join(os.getcwd(), "templates")
        self.templateLocation = argFileTemplate.get_template(os.path.join(templateDir,self.templateName))
        
    @staticmethod
    def get_template(filePath):
        try:
             os.path.isfile(filePath)
        except FileNotFoundError:
            print("Template file not found")
        
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
        return os.path.join(rootFilePath, fileName)

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

# write user- and main program-defined values to the argFile
def write_file(filePath,fileStatus="",**kwargs):
    try:
        fileStatus == "w" or fileStatus == "a"
    except ValueError:
        print("Error: fileStatus must be `w` or `a`")
           
    shutil.copy(filePath, filePath+"~" )
    print("Writing the argfile " + filePath)
    # read in lines from the temporary sourceFile
    fileName = filePath+"~"
    with open(fileName) as f: 
        lines = f.readlines()
    f.close()
    # replace relevant lines with user-defined and preset values
    for index,line in enumerate(lines):
        #print(line)
        for key, value in kwargs.items():
            if key in line:
                #print key
                if 'setenv' in line:
                    lines[index] = 'setenv ' + str(key) + '' + str(value)
                else:
                    lines[index] = 'set ' + str(key) + ' = ' + str(value)           
    # write values to the argFile
    f = open(filePath, fileStatus)
    for line in lines:
        #print(line)
        if len(line.rstrip('\n')) > 0:
            f.write(line + '\n')          
    f.close()
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
    #print(pathParts[0])
    if not os.path.isdir(pathParts[0]):
        os.makedirs(pathParts[0])
        
    shutil.copyfile(srcPath,destPath)
    try:
        os.path.isfile(destPath)
    except FileNotFoundError:
        print("Error: file",destPath ,"not created")
    
def pexec(arg,*args):
    argList = []
    argList.append(arg)
 
    for a in args:
        argList.append(''.join(a)) 
    #print(argList)
    return subprocess.Popen(argList, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #return subprocess.run(arglist, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
   
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
        
    return freDir

# return the fre module file version currently loaded in the environment
def get_fre_version():
    moduleVersion=os.environ['MODULE_VERSION']
    hostName = get_host_name()
    if 'gfdl.noaa.gov' in hostName:
        moduleCmd = '/usr/local/Modules/' + moduleVersion + '/bin/modulecmd'
    elif 'gaea' in hostName:
        moduleCmd = '/opt/cray/pe/modules/' + moduleVersion + '/bin/modulecmd'
    
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

# create a time stamp to append to the temporary argFiles and directory.
def get_time_stamp(*args):
    #print(args)
    baseDir= get_fre_dir()
    
    cmd = os.path.join(baseDir.split("/site")[0],'sbin','time_stamp.csh')
    try:
        os.path.isfile(cmd)
    except FileNotFoundError:
        print("time_stamp.csh not found in the fre root directory")
    p = pexec(cmd,args)
    
     # Read stdout and print each new line
    sys.stdout.flush()
    for line in iter(p.stdout.readline, b''):
        sys.stdout.flush()
        # convert the byte object to a string
        lineStr = line.decode()
        #print(lineStr)
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

# execute find_module_info for hsm and return the directory 
# with the hsm module and the version of hsm on the system
def get_hsm_info():
    hsmModuleFilesDir = ""
    hsmVersion = ""

    p1 = subprocess.run(["which", "find_module_info"], 
                        stdout=subprocess.PIPE, universal_newlines=True)
    
    cmd = p1.stdout.rstrip()
    #print(cmd)
    if (cmd != ""):
        p2 = subprocess.run([cmd,"hsm"], stdout=subprocess.PIPE, universal_newlines=True)
        if (p2 != ""):
            args = p2.stdout.split()
            hsmModuleFilesDir = args[0]
            hsmVersion = args[2]
        return hsmModuleFilesDir, hsmVersion

# execute find_module_info for gcp and return the directory 
# with the gcp module and the version of gcp on the system
def get_gcp_info():
    xferToolModuleFilesDir = ""
    xferToolVersion = ""

    p1 = subprocess.run(["which", "find_module_info"], 
                        stdout=subprocess.PIPE, universal_newlines=True)
    
    cmd = p1.stdout.rstrip()
    #print(cmd)
    if (cmd != ""):
        p2 = subprocess.run([cmd,"gcp"], stdout=subprocess.PIPE, universal_newlines=True)
        if (p2 != ""):
            args = p2.stdout.split()
            xferToolModuleFilesDir = args[0]
            xferToolVersion = args[2]
        return xferToolModuleFilesDir, xferToolVersion
 
# Parse the command-line arguments
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-help", help='Generate an argFile with user-defined parameters and fre-defined \
                                     shell variables. Example with user-defined arguments: python3 fretransfer.py userDefs \
                                     -expName myExperiment -fileType history restart ascii -sourceDir /home/Dana.Scully/temp \
                                     -destDir /archive/Dana.Scully -destMachine gfdl -groupAccount gfdl_f\
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
                        dest = 'sourceDir',
                        help='Directory with ASCII, RESTART, and/or HISTORY sub-directories that contain the \
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
    parser_userDef.add_argument('-groupAccount', 
                        type=str,
                        required=True,
                        help='name of the gfdl group account (e.g., gfdl_f)')
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
                        type = str,
                        help='space-separated list of ascii file patterns to search for.\
                        User-specified pattern(s) replace the default list\
                        Ascii files containing the following patterns are transferred by default:\
                         "out","results", "log", "timestats", "stats", "velocity truncations" ')
    parser_userDef.add_argument('-restartPatterns', default=['.res.','.nc.', '.input.', '.tgz$', '.ww3$'],
                        nargs='?',
                        action='store',
                        type = str,
                        help='space-separated list of restart file patterns to search for. \
                        User-specified pattern(s) replace the default list. \
                        Restart files containing the following patterns are transferred by default:\
                         ".res.",".nc.", ".input.", ".tgz$", ".ww3$" ')
    parser_userDef.add_argument('-historyPatterns', default=['.nc.','.ww3$', '^rregion'],
                        nargs='?',
                        action='store',
                        type = str,
                        help='space-separated list of history file patterns to search for.\
                        User-specified pattern(s) replace the default list. \
                        History files containing the following patterns are transferred by default,\
                         "^rregion",".nc.",".ww3$" ')
    parser_userDef.add_argument('-stagingType',
                        choices=['Chained','Online'],
                        type = str,
                        action='store',
                        default='Chained',
                        help='output staging type. Default is "Chained".')
    parser_userDef.add_argument('-gridSpecFile',
                        type = str,
                        dest = 'gridSpec',
                        help='full path to the gridSpec file')

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
                        dest = 'sourceDir',
                        help='Directory with ASCII, RESTART, and/or HISTORY sub-directories that contain the \
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
                               help='Full path to the gridSpec file')
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
   
    # get the output.stager command
    p1 = subprocess.run(["which", "output.stager"],stdout=subprocess.PIPE, universal_newlines=True)
    outputStager = p1.stdout.rstrip()
    #print(outputStager)

    # directory with the templates; assumes you are in the fretransfer repo directory
    homeDir = os.getcwd()
    templateDir = os.path.join(homeDir, "templates")
    if (not os.path.exists(templateDir)):
        errMesg = "Error: template directory " + templateDir + " does not exist"
        print(errMesg)
        sys.stderr.write(errMesg)
        sys.exit(2)

    # create argFiles with user-defined options
    if args.defCategory == 'userDefs':
        print('Parsing Userdefs')
    
        # make an argument dictionary
        argDict = {}
        for a in vars(args):
            argDict[a] = getattr(args,a)
           # print(argDict[a])
        # define the environment variables required by output.stager
        hsmModuleFilesDir, hsmVersion = get_hsm_info()
        argDict["hsmModuleFilesDir"] = hsmModuleFilesDir
        argDict["hsmVersion"] = hsmVersion
        xferToolModuleFilesDir, xferToolVersion = get_gcp_info()
        argDict["xferToolModuleFilesDir"] = xferToolModuleFilesDir 
        argDict["xferToolVersion"] = xferToolVersion
        argDict["freCommandsVersion"] = get_fre_version()
        user=os.getenv('USER')
        argDict["ptmpDir"] = os.path.join("/lustre/f2/scratch",user,"ptmp")
        argDict["mppnccombineOptString"] = '-64 -h 16384 -m'
        if args.gridSpec == None:
            argDict["gridSpec"] = '()'
        
        sourcePath = os.path.join(args.sourceDir)
        for ftype in args.fileType:
            try:
                os.path.exists(sourcePath)
            except NotADirectoryError:
                print ('Error: directory',sourcePath,'does not exist.')
            # instantiate a new argfile in the sourcePath directory
            A = argFile(ftype, sourcePath)
            # get the file appendix
            fileNameParts = A.newFileLocation.split('/')
            fileNameAppendix = ""
            for f in fileNameParts:
                if 'tmp' in f:
                    for i in f.split('.'):
                        if 'tmp' in f:
                           fileNameAppendix=f
                           break
            argDict["saveOptions"] = "(--mail-type=fail --chdir=/lustre/f2/dev/" + user + "/" + args.expName +\
                                 "/run/stdout --output=/lustre/f2/dev/" + user + "/" + args.expName +\
                                 "/run/stdout/%x.o%j --clusters=es --partition=ldtn --account=" + args.groupAccount +\
                                 " --job---name=" + args.expName + ".output.stager." + fileNameAppendix + ".AS" +\
                                 " --time=8:00:00 --mincpus=01)"

            argDict["xferOptions"] = "(--mail-type=fail --chdir=/lustre/f2/dev/" + user + "/" + args.expName +\
                                 "/run/stdout --output=/lustre/f2/dev/" + user + "/" + args.expName +\
                                 "/run/stdout/%x.o%j --clusters=es --partition=rdtn --account=" + args.groupAccount +\
                                 " --job---name=" + args.expName + ".output.stager." + fileNameAppendix + ".AT" +\
                                 " --time=16:00:00 --mincpus=01)"

            argDict["workDir"] = args.sourceDir

            # output.stager processes files in workDir/archDir
            argDict["archDir"] = ftype.upper()
                
            argDict["outputDirRemote"] = os.path.join(args.outputDirRemote,args.expName,ftype.upper())
            os.chdir(sourcePath)
        
            # clean out argFiles from the working directory
            clean_dir(sourcePath,['*.args*'])
            # copy the template file to the working directory
            copy_file(A.templateLocation,A.newFileLocation)
            # write values in the argDict to the argFile
            write_file(A.newFileLocation,"w",**argDict)
            
            # call output.stager and print the stdout log
            p=pexec(outputStager, A.newFileLocation)
            sys.stdout.flush()
            for line in iter(p.stdout.readline, b''):
                sys.stdout.flush()
                # convert the byte object to a string
                lineStr = line.decode()
                print(lineStr)

            # delete the argFile instance
            del A
            os.chdir(homeDir)
    # these arguments are intended for use with the fre workflow, and should be modified by fre developers as needed
    elif args.defCategory == 'freDefs':
        print('Parsing freDefs')
        # make a dictionary
        argDict = {}
        for a in vars(args):
            if a != 'fileType' and a != 'workDir':
                argDict[a] = getattr(args,a)
            #print('hello',str(argDict[a]))
        for ftype in args.fileType:
                
            sourcePath = os.path.join(args.workDir,ftype)
            try:
                os.path.exists(sourcePath)
            except NotADirectoryError:
                print ('Error: directory',sourcePath,'does not exist.')
        
            os.chdir(sourcePath)
            # check that one argFile already exists in the working directory 
            argFiles = [n for n in glob.glob('*.args') if os.path.isfile(n)]
            try:
                any(argFiles[0].strip())
            except FileNotFoundError:
                print('Error: no',fType,'argFile found in',sourcePath)
            try:
                 len(argFiles) == 1
            except FileExistsError:
                 print('Error: multiple',fType,'argFiles found in ',sourcePath)
            # write the fre definitions to the existing argFile
            filePath = os.path.join(sourcePath,argFiles[0])
            write_file(filePath,"w",**argDict)
            
        
 

main()
