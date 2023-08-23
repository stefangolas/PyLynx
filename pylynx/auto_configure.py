# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 16:05:29 2023

@author: stefa
"""

import shutil
import sys
import os

from .file_utils import MM4_data_path, universal_method_path
from .mm4_interface.workspace import deploy_to_workspace

def auto_configure():
    try:
        workspace_name = sys.argv[1:]
        workspace_name = ' '.join(workspace_name)
    except IndexError:
        raise Exception("No workspace name given. Please give a valid workspace name.")
        
    deploy_to_workspace(workspace_name)