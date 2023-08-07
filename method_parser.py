# -*- coding: utf-8 -*-
"""
Created on Sat Aug  5 13:40:10 2023

@author: stefa
"""

import os
import xml.etree.ElementTree as ET

def command_enum(key):
    tree = ET.parse("C:\\ProgramData\\MethodManager4\\Demo Workspace\\Methods\\method1.met")
    root = tree.getroot()
    
    target_node = root.find("Properties//Collection[@name='Steps']//Items")
    
    els = target_node.findall("Complex//Properties//Simple[@name='CommandName']")
    
    commands = [el.attrib['value'] for el in els]
    
    enum = commands.index(key)
    
    return enum
