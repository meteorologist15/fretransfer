#!/usr/bin/python3
# FRETRANSFER unit tests
import unittest
import argparse
import os
import tempfile
import shutil

class stringParsing(unittest.TestCase):
    def setUp(self):
        self.name = 'String Parsing Test'
    # Destroy any resources required during the test
    # Will always be run if setUp runs regardless of tests successes
    def tearDown(self):
        print("stringParsing tearDown")
        
    # Returns True if length of empty string is 0
    def test_string_len_zero(self):
        print('Testing empty string length')
        self.assertEqual(len(''),0)
    # Returns true if the string splits and matches 
    # the given output. 
    def test_split(self):
        print('Testing string split')      
        s = 'omg wtf bbq'
        self.assertEqual(s.split(), ['omg','wtf','bbq']) 
        with self.assertRaises(TypeError): 
            s.split(3) 
    def test_string_case(self):
        print('Testing string case')
        s ='FRE'
        self.assertTrue(s.isupper())
        self.assertFalse(s.islower())
        self.assertEqual(s.lower(),'fre')
    def test_substring_regex_find(self):
        print('Testing regex string search')      
        s1='history.res.nc'
        s2=".res*"
        s3='historyres.nc'
        self.assertRegex(s1,s2)
        self.assertNotRegex(s1,s3)
    def test_string_in_set(self):
        print('Testing string in set')      
        slist =  ['*res*','*nc*','*.input.*tgz','*.ww3']
        self.assertIn('*.input.*tgz',slist)
        self.assertNotIn('.input.',slist)

def create_parser():
    parser = argparse.ArgumentParser(...)
    parser.add_argument('-expName',type=str)
    parser.add_argument('-type',type=str)
    return parser
    
class ArgParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = create_parser()
    def tearDown(self):
        print("Parser test tearDown")

    def test_argument(self):
        print('Testing parser argument')
        parsed = self.parser.parse_args(['-expName', 'myExperiment'])
        self.assertEqual(parsed.expName, 'myExperiment')
        self.assertNotEqual(len(parsed.expName.strip()),0)
    def test_argument_in_options(self):
        print('Testing if parser argument is in options list')
        parsed = self.parser.parse_args(['-type', 'restart'])
        sopts = ['ascii','restart','history']
        self.assertIn(parsed.type, sopts)
    def test_argument_not_in_options(self):
        print('Testing if parser argument is not in options list')
        parsed = self.parser.parse_args(['-type', 'netcdf'])
        sopts = ['ascii','restart','history']
        self.assertNotIn(parsed.type, sopts)
        
class TestFileReadWrite(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        #print("File read/write tearDown")
        shutil.rmtree(self.test_dir)
        print('Removed file ',os.path.join(self.test_dir, 'test.txt'))
        self.assertFalse(os.path.exists(os.path.join(self.test_dir, 'test.txt')))
    def test_file_read_write(self):
        print('Testing temporary file read/write')
        # Create a file in the temporary directory
        f = open(os.path.join(self.test_dir, 'test.txt'), 'w')
        print('Created file ',os.path.join(self.test_dir, 'test.txt'))
        # Write something to it
        f.write('Live FRE or die hard.')
        f.close()
        # Reopen the file and check if what we read back is the same
        f = open(os.path.join(self.test_dir, 'test.txt'))
        self.assertEqual(f.read(), 'Live FRE or die hard.')
        self.assertNotEqual(f.read(),'Live FRE or diehard')
        f.close()
        
        
if __name__ == '__main__': 
    unittest.main() 