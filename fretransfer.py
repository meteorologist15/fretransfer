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

#fretransfer_dir = "/home/Kristopher.Rand/git/fretransfer/templates/"
fretransfer_dir = "/ncrc/home1/Kristopher.Rand/git/fretransfer/templates/"
template_names = ["historyArgfileTemplate.txt", "restartArgfileTemplate.txt", 
                  "asciiArgfileTemplate.txt"]
argFile_types = ["history", "restart", "ascii"]
templates = {k:fretransfer_dir + v for (k,v) in zip(argFile_types, template_names)}

#freRunArgCfg = "/home/Kristopher.Rand/git/fretransfer/freRunArgs.cfg"
freRunArgCfg = "/ncrc/home1/Kristopher.Rand/git/fretransfer/freRunArgs.cfg"
#freDefArgCfg = "/home/Kristopher.Rand/git/fretransfer/freDefArgs.cfg"
freDefArgCfg = "/ncrc/home1/Kristopher.Rand/git/fretransfer/freDefArgs.cfg"

config_userDefs = configparser.ConfigParser()
config_frerun = configparser.ConfigParser()

logging_format = '%(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=logging_format)


# Class for argFile to create with a template   
class argFile:
    """ 
    Builds a container around the attributes of an .args file, which references
    essential states of a FRE program, in this case, output.stager

    Inheritance: None
    """  
    def __init__(self, fileType, newFilePath, *args):
        """
        Initialize an object that creates attributes to the .args file using a
        template, which is checked for its existence.

        Parameters (3):
        - fileType (str): The type of .args file being created (i.e. history, 
                         restart, ascii)
        - newFilePath (str): Path of newly written .args file
        - *args: Additional arguments needed

        Returns:
        None

        """
    
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
        """
        Retrieve the file path of a newly created .args file

        Parameters(1):
        - rootFilePath(str): The base directory for the final location

        Returns (1):
        - Final path for the new .args file

        """

        fileName = argFile.get_new_file_name(self)
        return os.path.join(rootFilePath, self.fileType, fileName)

    
    @staticmethod
    def get_new_file_name(self):
        """
        Builds a string containing a date and time for the newly created
        .args file

        Parameters (0):
        - None

        Returns (1):
        - newFileName (str): String with a filename containing a time stamp
                             for history, restart, and ascii .args files

        """

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
        """
        Gather and store a list of all the files needed for staging
        via output.stager based upon the file type desired, i.e.
        history, restart, and ascii

        Parameters (2):
        - fileType (str): 'ascii', 'history', or 'restart'
        - filePatterns (str): General list of file patterns to investigate from

        Returns (0):
        - None

        """

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


def write_file(filePath, fileStatus="", **kwargs):
    """
    Write out the values of all the arguments listed in the temporary file
    to the new .args file

    Parameters (2)
    - fileStatus (str): In 'write' or 'append' mode. Must be either/or.
    - **kwargs: Unpacking of a dictionary with the key/value pairs of arguments

    Returns (0):
    - None

    """

    if fileStatus != "w":
        if fileStatus != "a":
            raise ValueError("fileStatus must be 'w' or 'a'")
           
    shutil.copy(filePath, filePath + "~" )

    # read in lines from the temporary sourceFile
    with open(filePath + "~", "r") as h:
        lines = h.readlines()

    # replace lines with values if they exist
    for key, value in kwargs.items():
        logging.info("%s %s" % (key, str(value)))
        for index, line in enumerate(lines):
            if key in line:
                if 'setenv'in line:
                    lines[index] = 'setenv ' + key + '' + str(value)
                else:
                    lines[index] = 'set ' + key + ' = ' + str(value)

                break
              
    # write values to argFile
    with open(filePath, fileStatus) as j:
        for line in lines:
            if len(line.strip()) > 0:
                j.write(line + "\n")

    # remove the temporary file
    filePathParts = os.path.split(filePath)
    clean_dir(filePathParts[0], [filePathParts[1] + '~'])


#Generator function which yields a list of names that match one or more of the patterns."""       
def multi_filter(names, patterns):
    """
    Generator function which yields a list of names that match one or more of the
    file patterns.

    Parameters (2)
    - names (str): A list of file strings all within the current working directory
    - patterns (str): A list of strings that describe a search filter for certain files

    Returns (1)
    - A list of all of the matched files based off the patterns given

    """

    fileList = []
    for name in names:
        for pattern in patterns:
            if fnmatch.fnmatch(name, pattern) and name not in fileList:
                fileList.append(name)
    return fileList

                
def clean_dir(pathName, removeFilePatterns):
    """
    Function to help clear a directory of unnecessary files based upon a search
    patterns

    Parameters (2):
    - pathName (str): The base directory for the deletion searching
    - removeFilePatterns (str): The patterns to identify files for removal

    Returns (0):
    - None

    """

    os.chdir(pathName)
    for pattern in removeFilePatterns:
        fileList = glob.glob(pattern)
        for file in fileList:
            os.remove(file)
    
               
def copy_file(srcPath, destPath):
    """
    Copies a new .args file to the appropriate path and creates directories
    if necessary.

    Paramters (2):
    - srcPath (str): Original path of .args file
    - destPath (str): New path of .args file copied from srcPath

    Returns (0):
    None

    """

    pathParts = os.path.split(destPath)
    if not os.path.isdir(pathParts[0]):
        os.makedirs(pathParts[0])
        
    shutil.copyfile(srcPath, destPath)
    if not os.path.isfile(destPath):
        raise FileNotFoundError("File %s was not created" % destPath)
   
 
def pexec(arg, *args):
    """
    Executes a command based upon the given subparser arguments

    Paramters (2):
    - arg (str): Initial argument
    - *args (list): List of arguments from subparser

    Returns (1)
    - A Python subprocess object

    """

    argList = []
    argList.append(arg)
 
    for a in args:
        argList.append(''.join(a)) 

    return subprocess.Popen(argList, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def get_host_name():
    """
    Retrieves the machine HOST name. Raises an error if the hostname is not
    GFDL, Gaea, or Theia.

    Parameters (0):
    - None

    Returns (1)
    - The machine HOST name

    """

    hostName = os.environ['HOST']
    if any([re.search(r, hostName) for r in ['gfdl.noaa.gov', 'gaea', 'theia']]):
        return hostName
    else:
        raise OSError('Error: $HOST is not gfdl, gaea, or theia. Exiting.')


def get_fre_dir():
    """
    Retrieve the directory containing the repository for the FRE source code and
    .args template files (their eventual final destination).

    Parameters (0):
    - None

    Returns (1):
    - The base FRE directory

    """

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
    """
    Retrieve the current FRE module version loaded in the environment.

    Parameters (0)
    - None

    Returns (1)
    - The FRE version loaded

    """

    moduleVersion = os.environ['MODULE_VERSION']

    moduleCmd = '/opt/cray/pe/modules/' + moduleVersion + '/bin/modulecmd'
    #moduleCmd = '/usr/local/Modules/' + moduleVersion + '/bin/modulecmd'
    p = pexec(moduleCmd, "tcsh", "list")

    # Read stdout and print each new line
    sys.stdout.flush()
    for line in iter(p.stdout.readline, b''):
        sys.stdout.flush()
        lineStr = line.decode()

        # search for the fre version
        if 'bronx-' in lineStr:
           useline = lineStr.strip()
           searchResult = re.search(r'(?<=fre/)\S*', lineStr)
           freVersion = searchResult.group(0)

           break
    
    return freVersion


def get_time_stamp(*args):
    """
    Function that creates a time stamp to append to the temporary argFiles and
    directory.

    Parameters (1):
    - *args: Argument string for the date

    Returns (1):
    - A datetime string to attach to the temp files

    """

    baseDir = get_fre_dir()
    
    cmd = os.path.join(baseDir.split("/site")[0], 'sbin', 'time_stamp.csh')
    if not os.path.isfile(cmd):
        raise FileNotFoundError("time_stamp.csh not found in the fre root directory")

    p = pexec(cmd, args)
    
    # Read stdout and print each new line
    sys.stdout.flush()
    for line in iter(p.stdout.readline, b''):
        sys.stdout.flush()
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
    """
    Helper function that inserts individual "sections" of a config file
    into an argparse object via its method "add_argument". It places
    the key, value pairings of a section into a dictionary and unpacks
    that dictionary into ArgumentParser.add_argument(). Special key, value
    relationships containing Python reserved words must be maintained and
    are demarcated by a preceding underscore (_) in the config file. These
    are parsed via Python's 'eval' method after the underscore is removed.

    Parameters (2):
    - configparser_obj: An object from the configparser.ConfigParser() class
    - argparse_obj: An object from the argparse.ArgumentParser() class

    Returns (0):
    - None

    """

    for section in configparser_obj.sections():
        arg_dict = dict(configparser_obj[section])
        for key, value in arg_dict.items():
            if '_' in value:
                arg_dict[key] = eval(value.replace('_', ''))

        argparse_obj.add_argument(section, **arg_dict)


def get_sourcepath(args, ftype):
    """
    Helper function for main() which retrieves the source path of the
    working directory housing the 'ascii', 'history', and 'restart' files

    Parameters (2):
    - args: ArgParse object
    - ftype: The type of files fretransfer is dealing with

    Returns (1):
    - The path to the source directory.

    """

    if not (ftype == 'ascii' or ftype == 'restart' or ftype == 'history'):
        raise ValueError("Invalid file type. Must be 'history', 'ascii', or 'restart'")

    sourcePath = os.path.join(args.workDir, ftype)
    if not os.path.exists(sourcePath):
        raise NotADirectoryError("Directory %s does not exist!" % sourcePath)

    os.chdir(sourcePath)
    return sourcePath


def parse_args():
    """
    The core function for parsing arguments. Arguments for fretransfer,
    userDef arguments, and frerun arguments are defined and parsed here.
    The userDef and frerun arguments are grabbed from configuration files,
    which are located in the same directory as the argFile temporary files.

    Parameters (0):
    - None

    Returns (1):
    - The arguments from fretransfer

    """

    parser = argparse.ArgumentParser(description="Fretransfer generates a FRE-style argFile with user-defined parameters and FRE-defined \nshell variables and then passes these newly formed '.args' files to FRE's output.stager).\n\nExample with user-defined arguments:\npython3 fretransfer.py userDefs -expName foo_experiment -fileType history restart ascii\n-sourceDir /path/to/the/original/work/directory/where/fileTypes/are/located\n-destDir /path/to/the/destination/directory/ie/archive -destMachine gfdl -stagingType Chained\n\nExample with FRE-defined shell variables:\npython3 fretransfer.py freDefs -paramCheckSumOn 1'", formatter_class=argparse.RawTextHelpFormatter)
    """parser.add_argument("-help", help='Generate an argFile with user-defined parameters and fre-defined \
                                     shell variables. Example with user-defined arguments: python3 fretransfer.py userDefs \
                                     -expName myExperiment -fileType history restart ascii -sourceDir /home/Jessica.Liptak/temp \
                                     -destDir /archive/Firstname.Lastname -destMachine gfdl \
                                     Example with fre-defined shell variables: python3 fretransfer.py freDefs -paramCheckSumOn 1 ' ) """
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


def call_output_stager(*args):

    script_location = "/ncrc/home2/fms/local/opt/fre-commands/bronx-15/site/ncrc/bin/output.stager"
    for argFile in args:
        subprocess.call([script_location, argFile])
    

def main():
    """
    The meat of fretransfer. Creates an argFile object using a template and writes
    out a new .args file to the appropriate directory, given specific command-line
    arguments.

    Parameters (0):
    - None

    Returns (0):
    - None

    """

    args = parse_args()

    # set up argFiles with user-defined options  
    if args.defCategory == 'userDefs':
        logging.info('Parsing Userdefs')
    
        argDict = {}
        for a in vars(args):
            argDict[a] = getattr(args, a)
    
        for ftype in args.fileType:
            sourcePath = get_sourcepath(args, ftype)

            A = argFile(ftype, args.workDir)
                
            # clean out argFiles from the working directory
            clean_dir(os.path.split(A.newFileLocation)[0], ['*.args*'])
            # copy the template file to the working directory
            copy_file(A.templateLocation, A.newFileLocation)
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
            elif len(argFiles) > 1:
                raise FileExistsError("Multiple %s argFiles found in %s" % (ftype, sourcePath))

            # write the fre definitions to the existing argFile
            filePath = os.path.join(sourcePath, argFiles[0])
            write_file(filePath, "a", **argDict)

    call_output_stager()
            
        
if __name__ == '__main__': 

    main()

