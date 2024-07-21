import socket
import threading
import json
import random
import time

class UDPNode:
    def __init__(self, node_id, port, total_nodes):
        self.node_id = node_id
        self.port = port
        self.total_nodes = total_nodes
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', self.port))
        self.address = ('localhost', self.port)
        self.running = True
        self.lamport_clock = 0
        self.vector_clock = [0] * total_nodes
        self.gossiped_to = set()  # To keep track of gossiped nodes
        print(f"Node {self.node_id} bound to port {self.port}")

        # Start listening thread
        self.listener_thread = threading.Thread(target=self.listen)
        self.listener_thread.start()

    def increment_lamport_clock(self):
        self.lamport_clock += 1

    def increment_vector_clock(self):
        self.vector_clock[self.node_id] += 1

    def send_message(self, message, recipient_port):
        self.increment_lamport_clock()  # Increment before sending
        msg = json.dumps({
            'node_id': self.node_id,
            'type': 'private',
            'lamport_timestamp': self.lamport_clock,
            'message': message
        })
        self.sock.sendto(msg.encode(), ('localhost', recipient_port))
        print(f"[PrivateMessaging] Node {self.node_id} sent message: '{message}' with lamport timestamp {self.lamport_clock} to port {recipient_port} (Recipient Node: {self._get_node_id_from_port(recipient_port)})")

    def broadcast_message(self, message):
        self.increment_vector_clock()  # Increment vector clock before broadcasting
        msg = json.dumps({
            'node_id': self.node_id,
            'type': 'broadcast',
            'vector_timestamp': self.vector_clock,
            'message': message
        })
        for port in range(13000, 13010):
            if port != self.port:
                self.sock.sendto(msg.encode(), ('localhost', port))
        print(f"[Broadcast] Node {self.node_id} broadcasted message: '{message}' with vector timestamp {self.vector_clock}")

        # Gossip to 3 random nodes
        self.gossip_message(message)

    def gossip_message(self, message):
        all_ports = list(range(13000, 13010))
        all_ports.remove(self.port)
        random_ports = random.sample(all_ports, min(3, len(all_ports)))  # Select up to 3 random ports

        for port in random_ports:
            if port not in self.gossiped_to:
                self.gossiped_to.add(port)  # Mark this port as gossiped to
                self.send_message(message, port)
                print(f"[Gossip] Node {self.node_id} gossiped message: '{message}' to port {port} (Recipient Node: {self._get_node_id_from_port(port)})")

    def listen(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)  # Buffer size is 1024 bytes
                if data:
                    message = json.loads(data.decode())
                    if message['type'] == 'private':
                        self.handle_private_message(message, addr)
                    elif message['type'] == 'broadcast':
                        self.handle_broadcast_message(message, addr)
            except Exception as e:
                if self.running:  # Ignore exceptions if we are not running
                    print(f"Node {self.node_id} encountered an error: {e}")
                break

    def handle_private_message(self, message, addr):
        # Update Lamport clock
        self.lamport_clock = max(self.lamport_clock, message['lamport_timestamp']) + 1
        print(f"[PrivateMessaging] Node {self.node_id} received private message: '{message['message']}' with lamport timestamp {message['lamport_timestamp']} from {addr} (Sender Node: {message['node_id']})")

    def handle_broadcast_message(self, message, addr):
        received_vector = message['vector_timestamp']
        # Update the vector clock to be at least as large as the received vector timestamp
        self.vector_clock = [max(self.vector_clock[i], received_vector[i]) for i in range(self.total_nodes)]
        self.increment_vector_clock()
        print(f"[Broadcast] Node {self.node_id} received broadcast message: '{message['message']}' with vector timestamp {received_vector} from {addr} (Sender Node: {message['node_id']})")
        # After receiving a broadcast, gossip to random nodes
        self.gossip_message(message['message'])

    def _get_node_id_from_port(self, port):
        return port - 13000  # Calculate node ID from port number

    def close(self):
        self.running = False
        self.sock.close()
        self.listener_thread.join()
        print(f"Node {self.node_id} closed socket")

if __name__ == "__main__":
    total_nodes = 10
    ports = range(13000, 13010)
    nodes = [UDPNode(node_id=i, port=port, total_nodes=total_nodes) for i, port in enumerate(ports)]

    # Example interactions
    #nodes[0].send_message("Hello from Node 0", ports[1])  # Send message to Node 1
    #nodes[0].broadcast_message("Hey all, I'm Node Zero!") #broadcast from 0
 
    nodes[0].broadcast_message("This is a general message from Node Zero!")

    time.sleep(2)
    for node in nodes:
        node.close()