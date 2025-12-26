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
        raise Exception(f"Full exception stack trace: Labware {labware_name} not found, please select from the following:\n{labware_list}")
    
    labware_id = labware.find(".//Id").text
    category = labware.find(".//Category").text
    return labware_id, category

class MethodWorktable:
    
    def __init__(self, workspace_name):
        self.workspace_name = workspace_name
        self.workspace_method = f"{MM4_data_path}\\{workspace_name}\\Methods\\universal_method.met"
        self.method_tree = ET.parse(self.workspace_method)
        self.method_root = self.method_tree.getroot()

    def _get_items_node(self, loc_node):
        """
        Helper to get the inner <Items> node where labware definitions live, 
        starting from the location's <Complex> node.
        Path: Complex/Properties/Collection[@name='LabwareStackElems']/Items
        """
        # Search relative to the location node for the final <Items> collection.
        return loc_node.find("./Properties/Collection[@name='LabwareStackElems']/Items")

    def get_location_by_name(self, loc_name):
        """
        Finds the location node (<Complex>) in the method file by its LocationName attribute.
        Uses iteration over results instead of unreliable parent navigation.
        """
        # Find all resource stacks across all defined worktables
        # We search for all <Complex> elements that are children of a <Items> collection
        # under ResourceStacks/Items.
        # This is robust but might be slow if the XML is huge.
        
        # We need to find the node that CONTAINS the matching LocationName.
        # Let's search all ResourceStacks collections in the entire document.
        
        # 1. Find all ResourceStacks container nodes (Left and Right Worktables)
        resource_maps = self.method_root.findall(".//Collection[@name='ResourceStacks']/Items")

        # 2. Iterate through all possible resource stacks in the map
        for stacks_container in resource_maps:
            # 3. Iterate through all individual location nodes (<Complex>) in that container
            for loc_node in stacks_container.findall("./Complex"):
                # 4. Check if the LocationName child matches the target name
                # Structure: <Complex>/<Properties>/<Simple name="LocationName" value="..."/>
                name_node = loc_node.find("./Properties/Simple[@name='LocationName']")
                
                if name_node is not None and name_node.attrib.get('value') == loc_name:
                    return loc_node  # Return the correct <Complex> location node

        return None # Location not found in any resource map
    
    def show_worktable(self):
        """
        Shows the current labware loaded on the worktable based on the method XML.
        Uses a robust XPath to find the ResourceStacks regardless of the outer path.
        """
        # Robustly find all worktable definition complexes
        worktables = self.method_root.findall(".//Collection[@name='WorktableResourceMaps']/Items/Complex")
        
        for wt in worktables:
            wt_name_node = wt.find(".//Simple[@name='WorktableName']")
            if wt_name_node is None:
                continue
                
            wt_name = wt_name_node.attrib['value']
            print(f"--- Worktable: {wt_name} ---")
            
            resource_stacks = wt.find(".//Collection[@name='ResourceStacks']/Items")
            
            if resource_stacks is not None:
                # loc is the <Complex> node representing the deck position
                for loc in resource_stacks.findall("./Complex"):
                    
                    location_name_node = loc.find(".//Simple[@name='LocationName']")
                    if location_name_node is None:
                        continue
                        
                    name = location_name_node.attrib['value']
                    resources = self._get_items_node(loc)
                    
                    print(f"Location: {name}")
                    if resources is not None:
                        # res is the <Complex> node representing the labware item
                        for res in resources.findall("./Complex"):
                            labware_name_node = res.find(".//Simple[@name='Name']")
                            labware_type_node = res.find(".//Simple[@name='LabwareName']")
                            
                            if labware_name_node is not None and labware_type_node is not None:
                                labware_name = labware_name_node.attrib['value']
                                labware_type = labware_type_node.attrib['value']
                                print(f"\tName: {labware_name}, Labware type: {labware_type}")
            
    
    def create_location_node(self, name, labware_name, labware_id, category, barcode = ""):
        complex_node = ET.Element('Complex')
        properties = ET.SubElement(complex_node, 'Properties')
        
        properties.append(ET.Element('Simple', {'name': 'Name', 'value': name}))
        properties.append(ET.Element('Simple', {'name': 'BarcodeId', 'value': barcode}))
        properties.append(ET.Element('Simple', {'name': 'LabwareName', 'value': labware_name}))
        properties.append(ET.Element('Simple', {'name': 'LabwareId', 'value': labware_id}))
        properties.append(ET.Element('Simple', {'name': 'Category', 'value': category}))
        
        return complex_node
    
    
    def add_labware_to_location(self, name, labware_name, location, barcode = "", side = "Left"):
        
        loc_node = self.get_location_by_name(location)
        if not loc_node:
            locations = get_worktable_locations(self.workspace_name, side)
            raise Exception(f"""Location {location }not found, please select from the 
                            following locations:\n{locations}""")
                            
        # Use the robust helper function
        items_node = self._get_items_node(loc_node)
        
        labware_id, category = get_labware_data(self.workspace_name, labware_name)
        
        node = self.create_location_node(name, labware_name, labware_id, category, barcode = "")
        items_node.append(node)
    
    def remove_labware_from_location(self, name, location, side="Left"):
        loc_node = self.get_location_by_name(location)
        if not loc_node:
            locations = get_worktable_locations(self.workspace_name, side)
            raise Exception(f"""Location {location }not found, please select from the 
                            following locations:\n{locations}""")
                            
        # Use the robust helper function
        items_node = self._get_items_node(loc_node)

        complex_nodes = items_node.findall("./Complex")
        for complex_node in complex_nodes:
            # Check for Simple[@name='Name'] as this is the labware name within the stack
            name_node = complex_node.find(".//Simple[@name='Name']")
            if name_node is not None and name_node.get("value") == name:
                items_node.remove(complex_node)
    
    def remove_all_labware_from_location(self, location, side="Left"):
        loc_node = self.get_location_by_name(location)
        
        if loc_node is None:
            locations = get_worktable_locations(self.workspace_name, side)
            raise Exception(f"""Location {location }not found, please select from the 
                            following locations:\n{locations}""")
                            
        # Use the robust helper function
        items_node = self._get_items_node(loc_node)

        complex_nodes = items_node.findall("./Complex")
        for complex_node in complex_nodes:
            items_node.remove(complex_node)

    def clear_worktable(self, side="Left"):
        locations = get_worktable_locations(self.workspace_name, side)
        for location in locations:
            self.remove_all_labware_from_location(location, side=side)

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