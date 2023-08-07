# -*- coding: utf-8 -*-
"""
Created on Sat Jul 22 19:30:52 2023

@author: stefa
"""

import xml.etree.ElementTree as ET
import socket

def get_host_ip():    
    hostname=socket.gethostname()
    IPAddr=socket.gethostbyname(hostname)
    return IPAddr


def update_tcp_server_address():
    try:
        
        new_tcp_server_address = get_host_ip()
        xml_file_path = 'C:\\ProgramData\\MethodManager4\\methodmanager.server.config'
        # Parse the XML file
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        
        # Find the TcpServerAddress element
        for simple_element in root.findall('.//Simple[@name="TcpServerAddress"]'):
            simple_element.set('value', new_tcp_server_address)

        # Write the updated XML back to the file
        tree.write(xml_file_path)

        print(f'The TcpServerAddress has been updated to: {new_tcp_server_address}')
    except Exception as e:
        print(f'Error updating TcpServerAddress: {e}')



# Usage example:
update_tcp_server_address()
