# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 15:49:05 2023

@author: stefa
"""

import os
import re
import xml.etree.ElementTree as ET
from ..file_utils import universal_method_path, MM4_data_path, method_variables_path
from .method_parser import commands_list

generics = ['Go To Step','End If','If','Write To Output','Loop Until',
            'Import Worktable','String Builder', 'Begin Loop','Wait For Variable']


command_to_tool = lambda s: re.search(r'\((.*?)\)', s).group(1) if '(' in s else None

#---- XPATH Variables ------------------------------------------------------------#
method_worktables_xpath = ".//Properties//Collection[@name='WorktableResourceMaps']//Items"
method_steps_xpath = ".//Properties//Collection[@name='Steps']//Items"
step_name_xpath = ".//Properties//Simple[@name='CommandName']"
resource_stacks_xpath = ".//Properties//Collection[@name='ResourceStacks']//Items"
worktable_name_xpath = ".//Properties//Simple[@name='WorktableName']"
stack_name_xpath = ".//Properties//Simple[@name='LocationName']"

#--------------------------------------------------------------------------------#


def set_worktable_sides(sides, method_tree):
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
    workspace_files = os.listdir(f"{MM4_data_path}\\{workspace_name}\\Configuration")
    for side in 'Left', 'Right':
        side_exists = len([file for file in workspace_files if side in file])>0
        if side_exists:
            sides.append(side)
    return sides

def get_workspace_tools(workspace_name):
    tree = ET.parse(f"{MM4_data_path}\\{workspace_name}\\Configuration\\Lynx.config")
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

def map_method_locations(method_tree, workspace_name):
    """
    Replaces the generic LocationName values in the method XML with the
    physical location names found in the workspace's .Worktable.config file.
    
    This fixes the incompatibility between the method's hardcoded locations
    and the actual physical deck names (e.g., 'SCILA_01', 'Vspin') used
    in the configuration files.
    """
    method_root = method_tree.getroot()
    method_worktables = method_root.find(method_worktables_xpath)

    for wt in method_worktables:
        method_wt_side = get_worktable_side(wt)
        
        # 1. Get the list of actual physical location names for this side
        physical_loc_names = get_worktable_locations(workspace_name, method_wt_side)
        
        # 2. Get the resource stacks (locations) defined in the method XML
        method_stacks = wt.find(resource_stacks_xpath)

        # 3. Create a mapping for substitution: Map the method's generic index to the physical name
        # We assume the index order in the method file corresponds to the order in the config file.
        
        # The list comprehension ensures we only map as many locations as are defined in both files,
        # preventing an IndexError if one list is shorter than the other.
        mapping_count = min(len(method_stacks), len(physical_loc_names))
        
        # This list of tuples is the key: [(<Complex element>, 'SCILA_01'), ...]
        update_list = zip(method_stacks[:mapping_count], physical_loc_names[:mapping_count])
        
        for stack_node, physical_name in update_list:
            # Find the Simple element containing the LocationName
            location_name_node = stack_node.find(stack_name_xpath)
            
            if location_name_node is not None:
                # Update the LocationName attribute in the method XML
                location_name_node.attrib['value'] = physical_name
                
    return method_tree

def get_worktable_locations(workspace_name, side):
    workspace_worktable = ET.parse(f"{MM4_data_path}\\{workspace_name}\\Configuration\\Lynx.{side}.Worktable.config")
    ws = workspace_worktable.getroot()
    ws_locs = [name.text for name in ws.findall(".//Name")]
    ws_locs = [loc for loc in ws_locs if "WORKTABLESOURCETAG" not in loc]

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

def clear_method_variables(workspace_name):
    workspace_variables_path = f"{MM4_data_path}\\{workspace_name}\\WorkspaceVariables.config"
    tree = ET.parse(workspace_variables_path)
    workspace_vars_root = tree.getroot()
    variables = workspace_vars_root.find(".//Variables")
    for v in variables:
        v.find(".//Value").text = None
    tree.write(workspace_variables_path)
        
def list_workspace_vars(workspace_vars_root):
    variables = workspace_vars_root.find(".//Variables")
    list_of_vars = []
    for v in variables:
        v_name = v.find(".//Name").text
        list_of_vars.append(v_name)
    return list_of_vars


def add_method_variables(workspace_name):
    workspace_variables_path = f"{MM4_data_path}\\{workspace_name}\\WorkspaceVariables.config"
    workspace_vars_tree = ET.parse(workspace_variables_path)
    workspace_vars_root = workspace_vars_tree.getroot()
    ws_variables_node = workspace_vars_root.find(".//Variables")
    workspace_vars = list_workspace_vars(workspace_vars_root)
    
    method_vars_tree = ET.parse(method_variables_path)
    
    method_vars_root = method_vars_tree.getroot()
    variables = method_vars_root.find(".//Variables")
    for v in variables:
        v_name = v.find(".//Name").text
        if v_name not in workspace_vars:
            ws_variables_node.append(v)
    
    workspace_vars_tree.write(workspace_variables_path)
        

def deploy_to_workspace(workspace_name):
    """
    Configure the universal method to be compatible
    with a workspace and then deploy it to that workspace
    """
    
    method_tree = ET.parse(universal_method_path)
    
    sides = get_workspace_sides(workspace_name)
    method_tree = set_worktable_sides(sides, method_tree)
    method_tree = remove_incompatible_commands(workspace_name, method_tree)
    
    method_tree = map_method_locations(method_tree, workspace_name)
    
    method_tree = set_worktable_capacity(workspace_name, method_tree)
    
    workspace_path = os.path.abspath(f"{MM4_data_path}\\{workspace_name}")
    method_path = os.path.join(workspace_path, "Methods", "universal_method.met")
    method_tree.write(method_path)
    
    add_method_variables(workspace_name)



    


