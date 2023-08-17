# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 15:08:19 2023

@author: stefa
"""
from pylynx import VVPArray

def normalize(c1_Array, v1, c2):
    """
    Returns a VVPArray for the dispense volumes to normalize wells
    with concentrations in c1_Array.
    
    Args:
        c1_Array : Pandas dataframe of concentrations
        v1: Starting volume
        c2: Desired final concentration
        
    Returns:
        VVPArray of dispense volumes to normalize

    """
    
    # Assuming v1 is equal for all wells
    dispense_Array = c1_Array*v1/c2 - v1
    dispense_Array[dispense_Array < 0] = 0
    dispense_Array = VVPArray(dispense_Array)
    return dispense_Array
    