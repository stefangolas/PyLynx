# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 09:56:41 2023

@author: stefa
"""

import xml.etree.ElementTree as ET


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