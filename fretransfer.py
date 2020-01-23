#!/usr/bin/env python3

# FRETRANSFER
# this is the main fretransfer script
# example: python3 fretransfer -expName mom6_solo_global_ALE_z -fileType history  
# -sourceDir /home/sourceDirectory -destDir /archive/Firstname.Lastname -destMach gfdl
###########################################################################################
import configparser
import subprocess
import argparse
import datetime
import logging
import fnmatch
import shutil
import glob
import sys
import re
import os

fretransfer_dir = "/home/Kristopher.Rand/git/fretransfer/templates/"
template_names = ["historyArgfileTemplate.txt", "restartArgfileTemplate.txt", 
                  "asciiArgfileTemplate.txt"]
argFile_types = ["history", "restart", "ascii"]
templates = {k:fretransfer_dir + v for (k,v) in zip(argFile_types, template_names)}

freRunArgCfg = "/home/Kristopher.Rand/git/fretransfer/freRunArgs.cfg"
freDefArgCfg = "/home/Kristopher.Rand/git/fretransfer/freDefArgs.cfg"

config_userDefs = configparser.ConfigParser()
config_frerun = configparser.ConfigParser()

logging_format = logging_format = '%(levelname)s: %(message)s'
logging.basicConfig(level = logging.INFO, format = logging_format)


# Class for argFile to create with a template   
class argFile:
 
    def __init__(self, fileType, newFilePath, *args):
    
        self.fileType = fileType

        if os.path.isfile(templates[fileType]):
            self.templateLocation = templates[fileType]
        else:
            raise FileNotFoundError("The %s template file %s does not exist." % (fileType, templates[fileType]))

        filePatterns = []
        # get the full path of new argFile 
        self.newFileLocation = argFile.new_file(self, newFilePath)

        # get list of files to process
        argFile.get_file_list(self, self.fileType, filePatterns)
 
    
    # each new file has a rootFilePath set to None by default    
    # the new file is placed in {newFilePath}/{fileType}
    @staticmethod
    def new_file(self, rootFilePath):

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

        newFileName = fileNameRoot + fileNameAppendix
        return newFileName
    
    @staticmethod
    def get_file_list(self, fileType, filePatterns):

        if any(filePatterns):
           patternMatch = filePatterns
        elif fileType == 'ascii': 
           patternMatch = ['*out','*results*','*log*','*timestats*','*stats*','*velocity_truncations*']
        elif fileType == 'restart':
            patternMatch = ['*res*','*nc*','*.input.*tgz','*.ww3']
        elif fileType == 'history':
            patternMatch = ['*nc*','*.ww3']
        
        names = os.listdir('.')
        self.fileList = multi_filter(names, patternMatch)


# write the data to the file
def write_file(filePath, fileStatus="", **kwargs):

    if fileStatus != "w":
        if fileStatus != "a":
            raise ValueError("Error: fileStatus must be 'w' or 'a'")
           
    shutil.copy(filePath, filePath + "~" )

    # read in lines from the temporary sourceFile
    source = open(filePath + "~", "r" )
    lines = []

    for line in source:
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
    clean_dir(filePathParts[0], [filePathParts[1] + '~'])


#Generator function which yields a list of names that match one or more of the patterns."""       
def multi_filter(names, patterns):

    fileList = []
    for name in names:
        for pattern in patterns:
            if fnmatch.fnmatch(name, pattern) and name not in fileList:
                fileList.append(name)
    return fileList

                
# delete file(s) in a directory
def clean_dir(pathName, removeFilePatterns):

    os.chdir(pathName)
    for pattern in removeFilePatterns:
        fileList = glob.glob(pattern)
        for file in fileList:
            os.remove(file)
    
               
def copy_file(srcPath, destPath):

    pathParts = os.path.split(destPath)
    if not os.path.isdir(pathParts[0]):
        os.makedirs(pathParts[0])
        
    shutil.copyfile(srcPath, destPath)
    if not os.path.isfile(destPath):
        raise FileNotFoundError("File %s was not created" % destPath)
   
 
def pexec(arg, *args):

    argList = []
    argList.append(arg)
 
    for a in args:
        argList.append(''.join(a)) 

    return subprocess.Popen(argList, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)


# determine the location of the host machine
def get_host_name():

    hostName = os.environ['HOST']
    if any([re.search(r, hostName) for r in ['gfdl.noaa.gov', 'gaea', 'theia']]):
        return hostName
    else:
        raise OSError('Error: $HOST is not gfdl, gaea, or theia. Exiting.')


# determine the location of the Fre source code and corresponding argFile templates
# assumes that argFile templates will be placed in the fre-commands directory on the host machine
def get_fre_dir():

    hostName = get_host_name()
    freVersion = get_fre_version()
    if 'gfdl.noaa.gov' in hostName:
        freDir = '/home/fms/local/opt/fre-commands/' + freVersion + '/site/gfdl-ws'
    elif 'gaea' in hostName:
        freDir = '/ncrc/home2/fms/local/opt/fre-commands/'  + freVersion + '/site/ncrc_common'
    elif 'theia' in hostName:
        freDir = '/home/fms/local/opt/fre-commands/' + freVersion +  '/site/theia' 
        
    return freDir


# return the fre module file version currently loaded in the environment
def get_fre_version():

    moduleVersion = os.environ['MODULE_VERSION']
   
    moduleCmd = '/usr/local/Modules/' + moduleVersion + '/bin/modulecmd'
    p = pexec(moduleCmd,"tcsh", "list")

    # Read stdout and print each new line
    sys.stdout.flush()
    for line in iter(p.stdout.readline, b''):
        sys.stdout.flush()
        # convert the byte object to a string
        lineStr = line.decode()
        # search for the fre version
        if 'bronx-' in lineStr:
           useline = lineStr.strip()
           searchResult = re.search(r'(?<=fre/)\S*', lineStr)
           freVersion = searchResult.group(0)

           break
    
    return freVersion


# create a time stamp to append to the temporary argFiles and directory.
def get_time_stamp(*args):

    baseDir= get_fre_dir()
    
    cmd = os.path.join(baseDir.split("/site")[0],'sbin','time_stamp.csh')
    if not os.path.isfile(cmd):
        raise FileNotFoundError("time_stamp.csh not found in the fre root directory")

    p = pexec(cmd, args)
    
     # Read stdout and print each new line
    sys.stdout.flush()
    for line in iter(p.stdout.readline, b''):
        sys.stdout.flush()
        # convert the byte object to a string
        lineStr = line.decode()
         # return a string appendix `tmp(DOY)(HHMMSS)`
        if 'no_time_stamp' in lineStr:
           wereAtNowNow = datetime.datetime.now()
           dateStr = wereAtNowNow.strftime("%Y.%m.%d")
           dt = datetime.datetime.strptime(dateStr, "%Y.%m.%d")
           tt = dt.timetuple()
          
           dateStr = "tmp" + str(tt.tm_yday) + wereAtNowNow.strftime("%H%M%S")
           break
        else:
           dateStr = lineStr.strip()
           break
       
    return dateStr


def add_argparse_arguments(configparser_obj, argparse_obj):

    for section in configparser_obj.sections():
        arg_dict = dict(configparser_obj[section])
        for key, value in arg_dict.items():
            if '_' in value:
                arg_dict[key] = eval(value.replace('_', ''))

        argparse_obj.add_argument(section, **arg_dict)



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

    if not os.path.exists(freDefArgCfg):
        raise FileNotFoundError("The configuration file for 'freDefs' arguments does not exist")

    with open(freDefArgCfg, 'r') as f:
        config_userDefs.read_file(f)

    add_argparse_arguments(config_userDefs, parser_userDef)

    # sub-parser for shell variables set by frerun
    parser_frerun = subparsers.add_parser('freDefs', help='Shell variables set by `frerun`.')

    if not os.path.exists(freRunArgCfg):
        raise FileNotFoundError("The configuration file for 'frerun' arguments does not exist.")

    with open(freRunArgCfg, 'r') as g:
        config_frerun.read_file(g)

    add_argparse_arguments(config_frerun, parser_frerun)

    args = parser.parse_args()

    return args


def get_sourcepath(args, ftype):

    if not (ftype == 'ascii' or ftype == 'restart' or ftype == 'history'):
        raise ValueError("Invalid file type. Must be 'history', 'ascii', or 'restart'")

    sourcePath = os.path.join(args.workDir, ftype)
    if not os.path.exists(sourcePath):
        raise NotADirectoryError("Directory %s does not exist!" % sourcePath)

    os.chdir(sourcePath)
    return sourcePath


def main():

    # parse the arguments
    args = parse_args()
    # set up argFiles with user-defined options
  
    if args.defCategory == 'userDefs':
        logging.info('Parsing Userdefs')
    
    # make a dictionary
    argDict = {}
    for a in vars(args):
        argDict[a] = getattr(args, a)
    
    for ftype in args.fileType:
        sourcePath = get_sourcepath(args, ftype)

        A = argFile(ftype, '/home/Jessica.Liptak/temp')
        
        # clean out argFiles from the working directory
        clean_dir(os.path.split(A.newFileLocation)[0], ['*.args*'])
        # copy the template file to the working directory
        copy_file(A.templateLocation,A.newFileLocation)
        # write values in the argDict to the argFile
        write_file(A.newFileLocation, "w", **argDict)
        
    elif args.defCategory == 'freDefs':

        logging.info('Parsing freDefs')
        argDict = {}

        for a in vars(args):
            if a != 'fileType' and a != 'workDir':
                argDict[a] = getattr(args, a)

        for ftype in args.fileType:
            sourcePath = get_sourcepath(args, ftype)

            # check that one argFile already exists in the working directory 
            argFiles = [n for n in glob.glob('*.args') if os.path.isfile(n)]

            if len(argFiles) == 0:
                raise FileNotFoundError("No %s argFile found in %s" % (ftype, sourcePath))
            elif len(argFiles > 1):
                raise FileExistsError("Multiple %s argFiles found in %s" % (ftype, sourcePath))

            # write the fre definitions to the existing argFile
            filePath = os.path.join(sourcePath, argFiles[0])
            write_file(filePath, "w", **argDict)
            
        
if __name__ == '__main__': 

    main()

