# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 16:16:16 2023

@author: stefa
"""
import os
import shutil


MM4_data_path = os.path.abspath("C:\ProgramData\MethodManager4")
this_file_dir = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.abspath(os.path.join(this_file_dir))
EXAMPLE_DIR = os.path.join(PACKAGE_DIR, 'example_scripts', 'basic_example')
universal_method_path = os.path.join(PACKAGE_DIR, 'mm4_files', 'universal_method.met')


def copy_files(source_dir, destination_dir):
    # Iterate through all files in the source directory
    for filename in os.listdir(source_dir):
        source_file = os.path.join(source_dir, filename)
        
        # Check if the item is a file
        if os.path.isfile(source_file):
            destination_file = os.path.join(destination_dir, filename)
            shutil.copy2(source_file, destination_file)
