#!/usr/bin/python3
# FRETRANSFER
# this is the main fretransfer script
# example: python3 fretransfer -expName mom6_solo_global_ALE_z -fileType history  
# -sourceDir /home/sourceDirectory -destDir /archive/Firstname.Lastname -destMach gfdl
###########################################################################################
import argparse
import sys
import os
import re
import subprocess
import shutil

# Class for managing  argFile templates
class argFileTemplate:
    
    def __init__(self, fileType):
        self.fileType=fileType
        self.templateName = self.fileType + 'ArgfileTemplate.txt'
        templateDir=get_fre_dir()
        self.templateLocation = get_template(templateDir + '/' + self.templateName)
    def get_template(filePath=None):
        try:
             os.path.isfile(filePath)
        except FileExistsError:
            print("Template file not found")
        
        return filepath
    
# Class for argFile to create with a template   
class argFile(argFileTemplate):
 
    def __init__(self,fileType,newFilePath):
       argFileTemplate.__init__(self,fileType)
       newFilePath = new_file(self,filePath)
    
       copy_file(self.templateLocation,newFilePath)
    # each new file has a filePath set to None by default    
    def new_file(self,filePath=None):
        fileName =self.fileType + 'Argfile.txt'
        return os.path.join(filePath,fileName)

def copy_file(srcPath,destPath):
    shutil.copy(srcPath,destPath)
    
def pexec(*args):
    return subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)#.communicate()[0].rstrip()

# determine the location of the host machine
def get_hostname():
    hostName=os.environt['HOST']
    if 'gfdl.noaa.gov' | 'gaea' | 'theia' in hostName:
        return(hostName)
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
           print('Using fre/' + freVersion.strip())
           break
    
    return freVersion

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
    # optional arguments
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
    args = parser.parse_args()
    return args
    

# main program
def main():
  fre_root =""
  args = parse_args()
  for ftype in args.fileType:
      tpl=argFileTemplate(os.path.join(fre_root,ftype,'_argfile_template'))
      argFile = tpl.new_file()

      f = open(tpl,'a')
        
      f.close

main()
