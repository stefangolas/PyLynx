# -*- coding: utf-8 -*-
"""
Created on Sat Aug  5 13:40:10 2023

@author: stefa
"""

import os
import xml.etree.ElementTree as ET
from ..file_utils import universal_method_path


def commands_list():
    tree = ET.parse(universal_method_path)
    root = tree.getroot()
    
    target_node = root.find("Properties//Collection[@name='Steps']//Items")
    
    els = target_node.findall("Complex//Properties//Simple[@name='CommandName']")
    
    commands = [el.attrib['value'] for el in els]
    return commands

def command_enum(key):
    
    commands = commands_list()
    
    enum = commands.index(key)
    
    return enum

