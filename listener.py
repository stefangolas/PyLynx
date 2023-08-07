# -*- coding: utf-8 -*-
"""
Created on Sat Jun 24 22:22:34 2023

@author: stefa
"""
import socket

def listen_socket(ip_address, port):
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the IP address and port
    sock.bind((ip_address, port))

    # Listen for incoming connections
    sock.listen()

    print(f"Listening on {ip_address}:{port}")

    while True:
        # Accept a connection
        client_socket, client_address = sock.accept()
        print(f"Received connection from {client_address}")
        
        try:
            data = client_socket.recv(1024)
            if data:
                print(f"Received data from {client_address}: {data.decode()}")

        except ConnectionResetError:
            print(f"Connection with {client_address} was reset by the client.")

        finally:
            client_socket.close()


        # Handle the connection
        # You can add your own logic here to process the incoming data

        # Close the client socket
        client_socket.close()


listen_socket('10.0.0.28', 47001)
