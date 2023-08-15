# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 12:11:37 2023

@author: stefa
"""

from pylynx import LynxInterface, get_host_ip
import string

rows = string.ascii_uppercase[0:8]
cols = range(1, 13)

num_rows = 8
num_cols = 12

channel_data = [[12 + row*2, 0, 0, 0]
                for row in range(num_rows) for col in range(num_cols)]


ip = get_host_ip()
lynx = LynxInterface(ip=ip, port=47000, simulating=True)

lynx.setup()

worktable = lynx.load_worktable('test_worktable3.worktable')

tips = worktable.allocate_labware('tips_01')
plate = worktable.allocate_labware('plate_01')

lynx.load_tips(tips=tips)
response = lynx.aspirate_96_vvp(plate = plate, channel_data=channel_data)
response = lynx.dispense_96_vvp(plate = plate, channel_data=channel_data)
lynx.eject_tips(tips=tips)

lynx.gripper_move_plate(source = 'Loc_15', destination = 'Loc_06', gripper_side = 'Left')

worktable = lynx.load_worktable('test_worktable4.worktable')

lynx.tip_pickup_sv('tips_05', row = 2, column = 5)
lynx.aspirate_sv('plate_01', vol = 30, row = 1, column = 8)
lynx.dispense_sv('plate_01', vol = 30, row = 2, column = 2)
lynx.tip_eject_sv('tips_05', row = 2, column = 5)
