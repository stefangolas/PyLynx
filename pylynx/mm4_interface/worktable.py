# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 09:56:41 2023

@author: stefa
"""

import xml.etree.ElementTree as ET
import glob
import os

from ..file_utils import universal_method_path, MM4_data_path, method_variables_path
from .method_parser import commands_list
from .workspace import get_worktable_locations, resource_stacks_xpath

def append_tipboxes(labware_root):
    xml_files = glob.glob(os.path.join(f"{MM4_data_path}\\Labware", '*Tipbox*.config'))

    # Iterate through the XML files and concatenate their trees to the original root
    for xml_file in xml_files:
        tree = ET.parse(xml_file)
        root_to_append = tree.getroot()
        labware_root.extend(root_to_append)
    return labware_root


def list_labware(workspace_name):
    tree = ET.parse(f"{MM4_data_path}\\{workspace_name}\\User.Labware.config")
    labware_root = tree.getroot()
    labware_root = append_tipboxes(labware_root)
    
    labware = [el.find(".//Name").text for el in labware_root]
    
    return labware

def get_labware_data(workspace_name, labware_name):
    labware_tree = ET.parse(f"{MM4_data_path}\\{workspace_name}\\User.Labware.config")
    labware_root = labware_tree.getroot()
    labware_root = append_tipboxes(labware_root)
        
    try:
        labware = [el for el in labware_root if el.find(".//Name").text==labware_name][0]
    except IndexError:
        labware_list = list_labware(workspace_name)
        labware_list = "\n".join(labware_list)
        raise Exception(f"Labware {labware_name} not found, please select from the following:\n{labware_list}")
    
    labware_id = labware.find(".//Id").text
    category = labware.find(".//Category").text
    return labware_id, category

class MethodWorktable:
    
    def __init__(self, workspace_name):
        self.workspace_name = workspace_name
        self.workspace_method = f"{MM4_data_path}\\{workspace_name}\\Methods\\universal_method.met"
        self.method_tree = ET.parse(self.workspace_method)
        self.method_root = self.method_tree.getroot()
    
    def get_location_by_name(self, loc_name):
        locs = self.method_root.find(resource_stacks_xpath)
        for loc in locs:
            name = loc.find(".//Properties/Simple").attrib['value']
            if name == loc_name:
                return loc
    
    def show_worktable(self):
        locs = self.method_root.find(resource_stacks_xpath)
        for loc in locs:
            name = loc.find(".//Properties/Simple").attrib['value']
            resources = loc.find(".//Properties/Collection/Items")
            print(f"Location: {name}")
            for res in resources:
                name = res.find(".//Simple[@name='Name']").attrib['value']
                labware_name = res.find(".//Simple[@name='LabwareName']").attrib['value']
                print(f"\tName: {name}, Labware type: {labware_name}")
            
    
    def create_location_node(self, name, labware_name, labware_id, category, barcode = ""):
        complex_node = ET.Element('Complex')
        properties = ET.SubElement(complex_node, 'Properties')
        
        properties.append(ET.Element('Simple', {'name': 'Name', 'value': name}))
        properties.append(ET.Element('Simple', {'name': 'BarcodeId', 'value': barcode}))
        properties.append(ET.Element('Simple', {'name': 'LabwareName', 'value': labware_name}))
        properties.append(ET.Element('Simple', {'name': 'LabwareId', 'value': labware_id}))
        properties.append(ET.Element('Simple', {'name': 'Category', 'value': category}))
        
        return complex_node
    
    
    def add_labware_to_location(self, name, labware_name, location, barcode = ""):
        
        loc_node = self.get_location_by_name(location)
        if not loc_node:
            locations = get_worktable_locations(self.workspace_name, "Left")
            raise Exception(f"""Location {location }not found, please select from the 
                            following locations:\n{locations}""")
                            
        items_node = loc_node.find(".//Properties//Collection//Items")
        labware_id, category = get_labware_data(self.workspace_name, labware_name)
        
        node = self.create_location_node(name, labware_name, labware_id, category, barcode = "")
        items_node.append(node)
    
    def remove_labware_from_location(self, name, location):
        loc_node = self.get_location_by_name(location)
        if not loc_node:
            locations = get_worktable_locations(self.workspace_name, "Left")
            raise Exception(f"""Location {location }not found, please select from the 
                            following locations:\n{locations}""")
                            
        items_node = loc_node.find(".//Properties//Collection//Items")

        complex_nodes = items_node.findall(".//Complex")
        for complex_node in complex_nodes:
            name_node = complex_node.find(".//Simple[@name='Name']")
            if name_node is not None and name_node.get("value") == name:
                items_node.remove(complex_node)
    
    def remove_all_labware_from_location(self, location):
        loc_node = self.get_location_by_name(location)
        if not loc_node:
            locations = get_worktable_locations(self.workspace_name, "Left")
            raise Exception(f"""Location {location }not found, please select from the 
                            following locations:\n{locations}""")
                            
        items_node = loc_node.find(".//Properties//Collection//Items")

        complex_nodes = items_node.findall(".//Complex")
        for complex_node in complex_nodes:
            items_node.remove(complex_node)

    def clear_worktable(self):
        locations = get_worktable_locations(self.workspace_name, "Left")
        for location in locations:
            self.remove_all_labware_from_location(location)

    def save_worktable(self):
        self.method_tree.write(self.workspace_method)


class Labware:
    def __init__(self, name, product, resource_type):
        self.name = name
        self.product = product
        self.resource_type = resource_type

class Worktable:
    
    def __init__(self, file_path):
        self.tree = ET.parse(file_path)
        self.root = self.tree.getroot()
        self.allocated_labware = []
    
    def find_labware(self, labware_name):
        xpath_expression = f".//LabwareStackElems/MMLabwareVec[Name='{labware_name}']"
        target_node = self.root.find(xpath_expression)
        
        if target_node:
            return target_node
        else:
            raise Exception("No labware found with name " + labware_name)
    
    def allocate_labware(self, labware_name):
        address = self.find_labware(labware_name)
        product = address[2].text
        resource_type = address[4].text
        
        if address not in self.allocated_labware:
            self.allocated_labware.append(address)
            return Labware(labware_name, product, resource_type)
        else:
            raise Exception("Labware already allocated")


if __name__ == '__main__':
    w = Worktable('test_worktable.worktable')
    tips = w.allocate_labware('tips_0')
    plate = w.allocate_labware('plate_0')