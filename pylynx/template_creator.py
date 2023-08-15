# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 15:49:19 2023

@author: stefa
"""
import os
from .file_utils import copy_files, EXAMPLE_DIR


def create_project():
    current_dir = os.path.abspath(os.getcwd())
    print("Creating project template")
    copy_files(EXAMPLE_DIR, current_dir)
