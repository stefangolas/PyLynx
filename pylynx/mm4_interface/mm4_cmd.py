# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 23:08:00 2023

@author: stefa
"""

import socket
import json
import string
import time
import subprocess

from .mm4_errors import mm4_errors_dict
from .worktable import Worktable, Labware
from .configure_server import get_host_ip
from .method_parser import command_enum
from .vvp import VVPArray


mm4_exe = 'C:\\Program Files (x86)\\Dynamic Devices\\MethodManager4\\MethodManager.DX.exe'

num_rows = 8
num_cols = 12


class MM4Command:

    def __init__(self, cmd_name, cmd_key = '', default_params = None):
        """
        cmd_name: name of command in MM4
        """
        self.cmd_name = cmd_name
        self.cmd_key = cmd_key
        self.__dict__.update(default_params)

    def apply_cmd_params(self, new_params_dict):
        """ 
        Update default params dictionary with new parameters
        """
        cmd = dict(self.__dict__, **new_params_dict)

        # Check if any fields are empty or are not strings

        if any(cmd[key] == '' for key in cmd):
            print(cmd.values())
            raise Exception("Command dictionary must not have empty values")

        if any(not isinstance(value, str) for value in cmd.values()):
            raise Exception("Command dictionary must only contain strings")

        return cmd


load_tips_template = MM4Command(cmd_name='cmd_load_tips', 
                                cmd_key='Load Tips(VVP96)',
                                default_params={
                                    'tip_box': None,
                                    'tip_box_column': '0',
                                    'tip_box_row': '0',
                                    'load_tip_offset_z': '0',
                                    'load_tip_force': '30'
                                })

eject_tips_template = MM4Command(cmd_name='cmd_eject_tips', 
                                 cmd_key='Eject Tips(VVP96)',
                                 default_params={
                                     'tip_box': None,
                                     'tip_box_column': '0',
                                     'tip_box_row': '0',
                                     'eject_tip_offset_z': '0'
                                 })


aspirate_vvp_template = MM4Command(cmd_name='cmd_aspirate_vvp', 
                                   cmd_key='Aspirate(VVP96)',
                                   default_params={
                                       'asp_plate': None,
                                       'asp_data': None,
                                       'asp_row': '0',
                                       'asp_column': '0',
                                       'asp_offset_x': '0',
                                       'asp_offset_y': '0',
                                       'asp_offset_z': '0'
                                   })

mix_vvp_template = MM4Command(cmd_name='cmd_mix_vvp', 
                              cmd_key='Mix(VVP96)',
                              default_params={
                                  'mix_plate': None,
                                  'mix_vvp_data': None,
                                  'mix_cycles': None,
                                  'mix_blowout': None,
                                  'mix_row': '0',
                                  'mix_col': '0',
                                  'mix_offset_x': '0',
                                  'mix_offset_y': '0',
                                  'mix_offset_z': '0'
                              })


dispense_vvp_template = MM4Command(cmd_name='cmd_dispense_vvp',
                                   cmd_key='Dispense(VVP96)',
                                   default_params={
                                       'disp_plate': None,
                                       'disp_data': None,
                                       'disp_row': '0',
                                       'disp_column': '0',
                                       'disp_offset_x': '0',
                                       'disp_offset_y': '0',
                                       'disp_offset_z': '0'
                                   })

gripper_move_to_location_template = MM4Command(cmd_name='cmd_gripper_move_to_location',
                                               #cmd_key = 'Aspirate(VVP96)',
                                               default_params={
                                                   'gripper_move_location': None,  # Deck location e.g. Loc_01
                                                   'gripper_move_side': None, # left or right
                                                   'gripper_move_x_offset': '0',
                                                   'gripper_move_y_offset': '0',
                                               })

gripper_move_to_plate_template = MM4Command(cmd_name='cmd_gripper_move_to_plate',
                                            #cmd_key = 'Aspirate(VVP96)',
                                            default_params={
                                                'gripper_move_location': None,  # Plate location
                                                'gripper_move_side': None,  # left or right
                                                'gripper_move_x_offset': '0',
                                                'gripper_move_y_offset': '0',
                                            })


gripper_move_plate_template = MM4Command(cmd_name='cmd_gripper_move_plate',
                                         #cmd_key='Aspirate(VVP96)',
                                         default_params={
                                             'gripper_move_plate_source': None,  # Plate location
                                             'gripper_move_plate_destination': None,  # Deck location e.g. Loc_01
                                             'gripper_move_side': None,  # left or right
                                             'gripper_move_plate_offset_x': '0',
                                             'gripper_move_plate_offset_y': '0',
                                             'gripper_move_plate_offset_z': '0',
                                             'gripper_open_position': '-20',  # units: mm
                                             'gripper_close_position': '-40',  # units: mm
                                             # units: %
                                             'gripper_force_percent': '40',
                                             # units: %
                                             'gripper_trigger_percent': '20'
                                         })

gripper_move_lid_template = MM4Command(cmd_name='cmd_gripper_move_lid',
                                       #cmd_key='Aspirate(VVP96)',
                                       default_params={
                                           'gripper_move_plate_source': None,
                                           'gripper_move_plate_destination': None,
                                           'gripper_move_side': None,  # left or right
                                           'gripper_move_plate_offset_x': '0',
                                           'gripper_move_plate_offset_y': '0',
                                           'gripper_move_plate_offset_z': '0',
                                           'gripper_open_position': '-20',
                                           'gripper_close_position': '-40',
                                           'gripper_force_percent': '40',
                                           'gripper_trigger_percent': '20'
                                       })

gripper_put_plate_template = MM4Command(cmd_name='cmd_gripper_put_plate',
                                        #cmd_key='Aspirate(VVP96)',
                                        default_params={
                                            'gripper_move_side': None,
                                            'gripper_put_plate': None,
                                        })

gripper_put_lid_template = MM4Command(cmd_name='cmd_gripper_put_lid',
                                      default_params={
                                          'gripper_move_side': None,
                                          'gripper_put_plate': None,
                                      })


load_worktable_template = MM4Command(cmd_name='cmd_import_worktable',
                                     cmd_key='Import Worktable',
                                     default_params={
                                         'worktable_filename': '',
                                     })


aspirate_sv_template = MM4Command(cmd_name= 'cmd_384SV_asp',
                                  cmd_key = 'Aspirate(384SV)',
                                  default_params={
                                      'asp_plate': None,
                                      'asp_384SV_vol': None,
                                      'asp_384SV_pre_airgap': '0',
                                      'asp_384SV_post_airgap': '0',
                                      'asp_row': None,
                                      'asp_column': None,
                                      'asp_offset_x': '0',
                                      'asp_offset_y': '0',
                                      'asp_offset_z': '2'
                                  })

dispense_sv_template = MM4Command(cmd_name='cmd_384SV_disp',
                                  cmd_key = 'Dispense(384SV)',
                                  default_params={
                                      'disp_plate': None,
                                      'disp_vol': None,
                                      'disp_airgap': '0',
                                      'disp_row': None,
                                      'disp_column': None,
                                      'disp_offset_x': '0',
                                      'disp_offset_y': '0',
                                      'disp_offset_z': '2'
                                  })

tip_pickup_sv_template = MM4Command(cmd_name='cmd_384SV_load_tip',
                                    cmd_key = 'Load Tips(384SV)',
                                    default_params={
                                        'tip_box': None,
                                        'tip_box_column': None,
                                        'tip_box_row': None,
                                        'load_tip_offset_z': '2',
                                        'load_tip_force': '30'
                                    })

tip_eject_sv_template = MM4Command(cmd_name='cmd_384SV_eject_tip',
                                   cmd_key = 'Eject Tips(384SV)',
                                   default_params={
                                       'tip_box': None,
                                       'tip_box_column': None,
                                       'tip_box_row': None,
                                       'eject_tip_offset_z': '0'
                                   })
cmd_templates = [
    load_tips_template,
    eject_tips_template,
    aspirate_vvp_template,
    dispense_vvp_template,
    mix_vvp_template,
    load_worktable_template,
    gripper_move_to_location_template,
    gripper_move_plate_template,
    gripper_move_to_plate_template,
    gripper_move_lid_template,
    aspirate_sv_template,
    dispense_sv_template,
    tip_pickup_sv_template,
    tip_eject_sv_template
]


class LynxInterface:

    def __init__(self, ip, port, simulating):
        self.server_ip = ip
        self.port = port
        self.simulating = simulating

        self.start_method_enum = '1'
        self.get_method_state_enum = '3'
        self.get_last_method_result_enum = '4'
        self.get_app_state_enum = '5'
        self.set_variable_enum = '6'
        self.get_variable_enum = '7'
        self.watch_variable_enum = '8'
        self.watch_method_enum = '9'
        self.watch_initialize_enum = '14'
        self.watch_connect_enum = '16'

        self.password = 'Remote'
        self.method_name = 'universal_method'

    def setup(self):
        try:
            self.get_application_state() # Check if MM4 is open before trying to open it again
        except ConnectionRefusedError:
            subprocess.Popen([mm4_exe])
        time.sleep(3) # Needed to wait before pinging server
        if self.simulating:
            self.wait_for_simulation_mode()
        self.watch_method_mm4()
        self.start_method(self.method_name)

    def wait_for_simulation_mode(self):
        print("Waiting for simulation mode before starting")
        simulation_mode = False
        while not simulation_mode:
            r = self.get_application_state()
            simulation_mode = r['ApplicationState'] == 3
            time.sleep(1)

    def send_packet(self, payload):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.settimeout(10)
            self.sock.connect((self.server_ip, self.port))
            payload = json.dumps(payload)
            self.sock.sendall(payload.encode())
            response = self.sock.recv(4096).decode('UTF-8')
            response = json.loads(response)
            self.check_response(response)
        finally:
            self.sock.close()

        return response

    def check_response(self, r):
        if r["Error"] != 0:
            raise Exception(mm4_errors_dict[r["Error"]])


#------ API Calls ------------------------------------------------------------#

    def set_variable_mm4(self, name, value):
        payload = {'Command': self.set_variable_enum,
                   'ItemName': name,
                   'ItemValue': value,
                   'Password': self.password}
        self.send_packet(payload)

    def get_variable_mm4(self, name):
        payload = {'Command': self.get_variable_enum,
                   'ItemName': name,
                   'Password': self.password}
        response = self.send_packet(payload)
        return response

    def get_application_state(self):
        payload = {'Command': self.get_app_state_enum,
                   'Password': self.password}
        response = self.send_packet(payload)
        return response

    def watch_variable_mm4(self, variable):
        payload = {'Command': self.watch_variable_enum,
                   'ItemName': variable,
                   'ItemValue': 'WATCH47001',
                   'Password': self.password}
        response = self.send_packet(payload)
        return response

    def watch_method_mm4(self):
        payload = {'Command': self.watch_method_enum,
                   'ItemValue': 'WATCH47001',
                   'Password': self.password}
        response = self.send_packet(payload)
        return response

    def hardware_initialize_mm4(self):
        payload = {'Command': self.watch_initialize_enum,
                   'ItemValue': '47001',
                   'Password': self.password}
        response = self.send_packet(payload)
        return response

    def hardware_connect_mm4(self):
        payload = {'Command': self.watch_connect_enum,
                   'ItemValue': '47001',
                   'Password': self.password}
        response = self.send_packet(payload)
        return response

    def start_method(self, method):
        payload = {'Command': self.start_method_enum,
                   'ItemName': method,
                   'Password': self.password}
        response = self.send_packet(payload)
        return response

    def get_last_method_result(self, method):
        payload = {'Command': self.get_last_method_result_enum,
                   'ItemName': method,
                   'Password': self.password}
        response = self.send_packet(payload)
        return response


#------ MM4 API Wrappers ------------------------------------------------------------#

    def send_command(self, mm4_cmd_dict):
        for field in mm4_cmd_dict:
            self.set_variable_mm4(field, mm4_cmd_dict[field])
            
        # Use the key (name of the command in MM4) to find the step number in the universal method
        cmd_enum = command_enum(mm4_cmd_dict['cmd_key'])
        
        
        self.set_variable_mm4('go_to_step', cmd_enum)
        self.set_variable_mm4('new_command', '1')
        self.wait_for_command_finish()
        self.reset_cmd_vars(mm4_cmd_dict)
        self.set_variable_mm4('go_to_step', 2)

    def reset_cmd_vars(self, cmd_dict):
        for field in cmd_dict:
            self.set_variable_mm4(field, '')

    def reset_all_variables(self):
        for template in cmd_templates:
            self.reset_cmd_vars(template.__dict__)

    def wait_for_command_finish(self):
        command_finished = False
        r = self.get_variable_mm4('new_command')

        self.ensure_active_method(r)
        while not command_finished:
            r = self.get_variable_mm4('new_command')
            self.ensure_active_method(r)
            command_finished = r['Result'] == "0"
            time.sleep(0.1)

    def ensure_active_method(self, r):
        if r['MethodState'] == 4:
            raise Exception(
                "Method encountered an error. Check the logs for more information.")
        if r['MethodState'] == 1:
            raise Exception("No method running.")

    def vvp_command_builder(self, channel_data):
        channel_data = [[str(i) for i in well] for well in channel_data]
        channel_data = [';'.join(i) for i in channel_data]
        channel_data = ','.join(channel_data)
        channel_data = 'VI;12;8,' + channel_data
        return channel_data

    def command_builder(self, template, **kwargs):
        """
        Apply parameters to all required arguments to build a command ready
        to be sent to MM4
        """

        kwargs = {k: str(v) for k, v in kwargs.items()}

        params_dict = {}
        if kwargs:
            params_dict.update(kwargs)
        
        cmd = template.apply_cmd_params(params_dict)
        
        
        return cmd

#---- MM4 Commands ------------------------------------------------------------#
    def load_tips(self, tips: Labware):
        assert tips.resource_type == 'Tipbox', 'Eject location must be type tipbox'

        params_dict = {'tip_box': tips.name}

        cmd = load_tips_template.apply_cmd_params(params_dict)

        self.send_command(cmd)

    def aspirate_96_vvp(self, plate: Labware, array: VVPArray):
        channel_data = array.convert_to_cmd_data()

        params_dict = {'asp_plate': plate.name,
                       'asp_data': channel_data}

        cmd = aspirate_vvp_template.apply_cmd_params(params_dict)

        self.send_command(cmd)
        response = self.get_variable_mm4('Lynx.VVP96.Aspirate.Output')["Result"]
        return response

    def dispense_96_vvp(self, plate: Labware, array: VVPArray):

        channel_data = array.convert_to_cmd_data()

        params_dict = {'disp_plate': plate.name,
                       'disp_data': channel_data}

        cmd = dispense_vvp_template.apply_cmd_params(params_dict)

        self.send_command(cmd)
        response = self.get_variable_mm4('Lynx.VVP96.Dispense.Output')["Result"]
        return response


    def mix_96_vvp(self, plate, mix_data, mix_cycles, blowout_vol, **kwargs):
        cmd = self.command_builder(mix_vvp_template,
                                   mix_plate=plate,
                                   mix_cycles=mix_cycles,
                                   mix_blowout=blowout_vol,
                                   **kwargs)
        self.send_command(cmd)

    def eject_tips(self, tips: Labware):
        assert tips.resource_type == 'Tipbox', 'Eject location must be type tipbox'

        params_dict = {
            'tip_box': tips.name
        }

        cmd = eject_tips_template.apply_cmd_params(params_dict)

        self.send_command(cmd)

    def load_worktable(self, worktable_file):
        params_dict = {
            'worktable_filename': worktable_file
        }
        cmd = load_worktable_template.apply_cmd_params(params_dict)

        self.send_command(cmd)

        worktable = Worktable(worktable_file)
        return worktable

    def gripper_move_to_location(self, location, gripper_side, **kwargs):

        params_dict = {
            'gripper_move_location': location,
            'gripper_move_side': gripper_side,
            'cmd_key': f'Move To Location(Gripper{gripper_side})'
        }

        if kwargs:
            params_dict.update(kwargs)
        
        cmd = gripper_move_to_location_template.apply_cmd_params(params_dict)
        self.send_command(cmd)

    def gripper_move_plate(self, source, destination, gripper_side, **kwargs):
        cmd = self.command_builder(gripper_move_plate_template,
                                   gripper_move_plate_source = source,
                                   gripper_move_plate_destination = destination,
                                   gripper_move_side = gripper_side,
                                   cmd_key = f'Move Plate(Gripper{gripper_side})',
                                   **kwargs)
        
        self.send_command(cmd)

    def gripper_move_to_plate(self, location, gripper_side, **kwargs):
        cmd = self.command_builder(gripper_move_to_plate_template,
                                   gripper_move_location=location,
                                   gripper_move_side=gripper_side,
                                   cmd_key = f'Move To Plate(Gripper{gripper_side})',
                                   **kwargs)
        
        self.send_command(cmd)

    def gripper_move_lid(self, location, gripper_side, **kwargs):
        cmd = self.command_builder(gripper_move_lid_template,
                                   gripper_put_plate=location,
                                   gripper_move_side=gripper_side,
                                   cmd_key = f'Move Lid(Gripper{gripper_side})',
                                   **kwargs)
        
        self.send_command(cmd)

    def aspirate_sv(self, plate, row, column, vol, **kwargs):
        cmd = self.command_builder(aspirate_sv_template,
                                   asp_plate=plate,
                                   asp_column=column,
                                   asp_row=row,
                                   asp_384SV_vol=vol,
                                   **kwargs)
        
        self.send_command(cmd)

    def dispense_sv(self, plate, row, column, vol, **kwargs):
        cmd = self.command_builder(dispense_sv_template,
                                   disp_plate=plate,
                                   disp_row=row,
                                   disp_column=column,
                                   disp_vol=vol,
                                   **kwargs)
        self.send_command(cmd)

    def tip_pickup_sv(self, tip_box, column, row, **kwargs):
        cmd = self.command_builder(tip_pickup_sv_template,
                                   tip_box=tip_box,
                                   tip_box_column=column,
                                   tip_box_row=row,
                                   **kwargs)
        self.send_command(cmd)

    def tip_eject_sv(self, tip_box, column, row, **kwargs):
        cmd = self.command_builder(tip_eject_sv_template,
                                   tip_box=tip_box,
                                   tip_box_column=column,
                                   tip_box_row=row,
                                   **kwargs)
        self.send_command(cmd)


rows = string.ascii_uppercase[0:8]
cols = range(1, 13)


