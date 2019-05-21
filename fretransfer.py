#!/usr/bin/python3
# FRETRANSFER
# this is the main fretransfer script
# example: python3 fretransfer -expName mom6_solo_global_ALE_z -fileType history  
# -sourceDir /home/sourceDirectory -destDir /archive/Firstname.Lastname -destMach gfdl
###########################################################################################
import argparse
import sys
import os
# 
# Class for managing  argFile templates
class argFileTemplate(object):
    
    def __init__(self, argfile_template_path):
        self.template = get_template(argfile_template_path)
        
    def get_template(filepath=None):
        try:
             os.path.isfile(filepath)
        except FileExistsError:
            print("Template file not found")
        
        return filepath
    
    def new_file(self,filepath=None):
        return argFile(self, filepath)

class argFile(object):
    """ Class for subdocument to insert into master document """
    def __init__(self, tpl,docpath=None):
        self.tpl = tpl


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
