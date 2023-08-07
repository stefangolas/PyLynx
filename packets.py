# -*- coding: utf-8 -*-
"""
Created on Sat Jul 22 21:26:03 2023

@author: stefa
"""

import psutil

def find_client_connections(client_ip, client_port):
    connections = psutil.net_connections(kind="tcp")
    
    for conn in connections:
        if conn.status == psutil.CONN_ESTABLISHED and conn.laddr.ip == client_ip and conn.laddr.port == client_port:
            print(f"Destination IP: {conn.raddr.ip}, Destination Port: {conn.raddr.port}")

if __name__ == "__main__":
    # Set the client IP and port
    client_ip = "10.0.0.28"
    client_port = 47001

    find_client_connections(client_ip, client_port)
