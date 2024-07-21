import socket
import threading
import time
import json

class VectorClock:
    #get a vector clock size depending on n nodes (v1, .., vn)
    def __init__(self, node_id, total_nodes):
        self.clock = [0] * total_nodes
        self.node_id = node_id
 

def send_udp(message, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    client_socket.sendto(message.encode(), ('localhost',port))

if __name__ == "__main__":
    total_nodes = 3 
    node_id = 0
    vector_clock = VectorClock(node_id, total_nodes)

    send_udp("Goodbye universe", 12000)