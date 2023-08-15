# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 16:05:29 2023

@author: stefa
"""

import shutil
import sys
import os

from .file_utils import MM4_data_path, universal_method_path


def auto_configure():
    try:
        workspace_name = sys.argv[1:]
        workspace_name = ' '.join(workspace_name)
    except IndexError:
        raise Exception("No workspace name given. Please give a valid workspace name.")
        
        
    workspace_path = os.path.join(MM4_data_path, workspace_name)
    
    if not os.path.exists(workspace_path):
        raise Exception("Workspace not found.")
    
    workspace_methods_path = os.path.join(workspace_path, "Methods")

    shutil.copy2(universal_method_path, workspace_methods_path)