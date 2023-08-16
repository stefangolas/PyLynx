# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 23:14:16 2023

@author: stefa
"""
import pandas as pd
import numpy as np
import string


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

    
class VVPArray(pd.DataFrame):
    def __init__(self, data = np.zeros((8, 12)), columns=None, **kwargs):
        super().__init__(data, columns=columns, **kwargs)
        self._apply_alphabetical_index()

    def _apply_alphabetical_index(self):
        index_labels = list(string.ascii_uppercase)[:len(self)]
        self.index = index_labels

    def convert_to_cmd_data(self):
        flat_list = []
        for index, row in self.iterrows():
            flat_list.extend(row.tolist())
        
        channel_data = [str(well_vol) for well_vol in flat_list]
        #channel_data = [';'.join(well_vol) for well_vol in channel_data]
        channel_data = ','.join(channel_data)
        channel_data = 'VI;12;8,' + channel_data
        return channel_data

    def row(self, label):
        return self.loc[label]

    def col(self, index):
        return self.iloc[:, index]
    

