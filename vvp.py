# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 23:14:16 2023

@author: stefa
"""




class Well_VVP:
    
    def __init__(self, volume, 
                 pre_airgap = 0, 
                 post_airgap = 0, 
                 residual_vol = 0):
        
        self.volume = volume
        self.pre_airgap = pre_airgap
        self.post_airgap = post_airgap
        self.residual_vol = residual_vol
    
    def __str__(self):
        s = f"volume: {self.volume} uL"
        
        if self.pre_airgap>0:
            s += f"pre_airgap: {self.pre_airgap}"
        
        if self.post_airgap>0:
            s += f"post_airgap: {self.post_airgap}"

        if self.residual_vol>0:
            s += f"residual_vol: {self.residual_vol}"
        
        return s

    
class Array_VVP:
    
    
    def __init__(self, array):
        self.array = array
        self.num_rows = 8
        self.num_cols = 12
    
    def __str__(self):
        [el for el in self.array]
        return [el for el in self.array]

channel_data = [Well_VVP(volume = 20) for row in range(8) for col in range(12)]

array = Array_VVP(array = channel_data)