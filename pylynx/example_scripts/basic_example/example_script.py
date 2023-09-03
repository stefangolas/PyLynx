# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 12:11:37 2023

@author: stefa
"""

from pylynx import (LynxInterface, get_host_ip, VVPArray, MethodWorktable,
                    list_labware)
import numpy as np
import pandas as pd


data = np.zeros((8, 12))
data[:, :3] = 20
df = pd.DataFrame(data)
array = VVPArray(df)

worktable = MethodWorktable("Demo Workspace")

worktable.clear_worktable()
list_labware("Demo Workspace")
worktable.add_labware_to_location("tips_1", "LXB-96-950F", "Loc_02")
worktable.add_labware_to_location("plate_1", "96 Well Plate", "Loc_04")
worktable.add_labware_to_location("plate_2", "96 Well Plate", "Loc_06")
worktable.save_worktable()


ip = get_host_ip()
lynx = LynxInterface(ip=ip, port=47000, simulating=True)

lynx.setup()


lynx.load_tips(tips="tips_1")
response = lynx.aspirate_96_vvp(plate = "plate_1", array = array)
response = lynx.dispense_96_vvp(plate = "plate_2", array = array)
lynx.eject_tips(tips="tips_1")



lynx.tip_pickup_sv('tips_1', row = 2, column = 5)
lynx.aspirate_sv('plate_1', vol = 30, row = 1, column = 8)
lynx.dispense_sv('plate_1', vol = 30, row = 2, column = 2)
lynx.tip_eject_sv('tips_1', row = 2, column = 5)
