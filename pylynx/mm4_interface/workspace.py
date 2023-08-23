# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 15:49:05 2023

@author: stefa
"""

import os
import re
import xml.etree.ElementTree as ET
from ..file_utils import universal_method_path
from .method_parser import commands_list

generics = ['Go To Step','End If','If','Write To Output','Loop Until','String Builder', 'Begin Loop','Wait For Variable']


command_to_tool = lambda s: re.search(r'\((.*?)\)', s).group(1) if '(' in s else None

#---- XPATH Variables ------------------------------------------------------------#
method_worktables_xpath = ".//Properties//Collection[@name='WorktableResourceMaps']//Items"
method_steps_xpath = ".//Properties//Collection[@name='Steps']//Items"
step_name_xpath = ".//Properties//Simple[@name='CommandName']"
resource_stacks_xpath = ".//Properties//Collection[@name='ResourceStacks']//Items"
worktable_name_xpath = ".//Properties//Simple[@name='WorktableName']"
stack_name_xpath = ".//Properties//Simple[@name='LocationName']"

#--------------------------------------------------------------------------------#


def set_method_worktable(sides, method_tree):
    method_root = method_tree.getroot()
    method_worktables = method_root.find(method_worktables_xpath)
    
    for wt in method_worktables:
        wt_name = get_worktable_side(wt)
        if wt_name not in sides:
            method_worktables.remove(wt)
    
    return method_tree



def get_worktable_side(wt):
    wt_properties = wt.find(".//Properties")
    wt_properties = [prop.attrib for prop in wt_properties]
    wt_name = [prop['value'] for prop in wt_properties if prop['name'] == 'WorktableName'][0]
    return wt_name


def get_workspace_sides(workspace_name):
    sides = []
    workspace_files = os.listdir(f"C:\\ProgramData\\MethodManager4\\{workspace_name}\\Configuration")
    for side in 'Left', 'Right':
        side_exists = len([file for file in workspace_files if side in file])>0
        if side_exists:
            sides.append(side)
    return sides

# TODO make MM4 workspace directory parameterized by an environment variable
def get_workspace_tools(workspace_name):
    tree = ET.parse(f"C:\\ProgramData\\MethodManager4\\{workspace_name}\\Configuration\\Lynx.config")
    root = tree.getroot()
    tools = [el.text for el in root.findall(".//Name")]
    return tools


def find_incompatible_commands(steps_node, workspace_tools):
    steps_to_remove = []

    for step in steps_node:
        command_name = step.find(step_name_xpath).attrib['value']
        if command_name in generics:
            continue
        command_tool = command_to_tool(command_name)
        if command_tool not in workspace_tools:
            steps_to_remove.append(step)
    
    return steps_to_remove


def remove_incompatible_commands(workspace_name, method_tree):
    method_root = method_tree.getroot()
    steps_node = method_root.find(method_steps_xpath)
    workspace_tools = get_workspace_tools(workspace_name)
    
    steps_to_remove = find_incompatible_commands(steps_node, workspace_tools)   
    for step in steps_to_remove:
        steps_node.remove(step)
    
    return method_tree
        
def get_worktable_locations(workspace_name, side):
    workspace_worktable = ET.parse(f"C:\\ProgramData\\MethodManager4\\{workspace_name}\\Configuration\\Lynx.{side}.Worktable.config")
    ws = workspace_worktable.getroot()
    ws_locs = [name.text for name in ws.findall(".//Name")]
    return ws_locs


def find_unusable_deck_locations(method_worktable, workspace_name):
    """
    Compare a method worktable to a workspace worktable configuration and
    return unusable deck locations
    """

    method_stacks = method_worktable.find(resource_stacks_xpath)
    method_wt_side = method_worktable.find(worktable_name_xpath).attrib['value']
    
    ws_locs = get_worktable_locations(workspace_name, method_wt_side)    
    stacks_to_remove = []
    for stack in method_stacks:
        location_id = stack.find(stack_name_xpath).attrib['value']
        if location_id not in ws_locs:
            stacks_to_remove.append(stack)
    
    return stacks_to_remove


# TODO Python can't read XML in utf-16 encoding (manually change it to utf-8)
def set_worktable_capacity(workspace_name, method_tree):
    """
    Remove resource stacks (deck positions) from the worktable
    node in the method XML that don't exist in the workspace config
    """
    
    method_root = method_tree.getroot()
    method_worktables = method_root.find(method_worktables_xpath)

    for wt in method_worktables:
        method_stacks = wt.find(resource_stacks_xpath)
        stacks_to_remove = find_unusable_deck_locations(wt, workspace_name)        
        for stack in stacks_to_remove:
            method_stacks.remove(stack)

    return method_tree
            


def deploy_to_workspace(workspace_name):
    """
    Configure the universal method to be compatible
    with a workspace and deploy it
    """
    
    method_tree = ET.parse(universal_method_path)
    
    sides = get_workspace_sides(workspace_name)
    method_tree = set_method_worktable(sides, method_tree)
    method_tree = remove_incompatible_commands(workspace_name, method_tree)
    method_tree = set_worktable_capacity(workspace_name, method_tree)
    
    workspace_path = os.path.abspath(f"C:\\ProgramData\\MethodManager4\\{workspace_name}")
    method_path = os.path.join(workspace_path, "Methods", "universal_method.met")
    method_tree.write(method_path)



    


