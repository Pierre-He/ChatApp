import socket
import threading
import json

class UDPNode:
    def __init__(self, node_id, port):
        self.node_id = node_id
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', self.port))
        self.address = ('localhost', self.port)
        self.running = True
        self.lamport_clock = 0
        print(f"Node {self.node_id} bound to port {self.port}")

        # Start listening thread
        self.listener_thread = threading.Thread(target=self.listen)
        self.listener_thread.start()

    def increment_clock(self):
        self.lamport_clock += 1

    def send_message(self, message, recipient_port):
        self.increment_clock()
        msg = json.dumps({'node_id': self.node_id, 'timestamp': self.lamport_clock, 'message': message})
        self.sock.sendto(msg.encode(), ('localhost', recipient_port))
        print(f"Node {self.node_id} sent message: {message} with timestamp {self.lamport_clock} to port {recipient_port}")

    def broadcast_message(self, message):
        self.increment_clock()
        msg = json.dumps({'node_id': self.node_id, 'timestamp': self.lamport_clock, 'message': message})
        for port in range(13000, 13010):
            if port != self.port:
                self.sock.sendto(msg.encode(), ('localhost', port))
        print(f"Node {self.node_id} broadcasted message: {message} with timestamp {self.lamport_clock}")

    def listen(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)  # Buffer size is 1024 bytes
                if data:
                    message = json.loads(data.decode())
                    self.lamport_clock = max(self.lamport_clock, message['timestamp']) + 1
                    print(f"Node {self.node_id} received message: {message['message']} with timestamp {message['timestamp']} from {addr}")
            except Exception as e:
                if self.running:  # Ignore exceptions if we are not running
                    print(f"Node {self.node_id} encountered an error: {e}")
                break

    def close(self):
        self.running = False
        self.sock.close()
        self.listener_thread.join()
        print(f"Node {self.node_id} closed socket")

if __name__ == "__main__":
    # Specify the ports directly
    ports = range(13000, 13010)
    nodes = [UDPNode(node_id=i, port=port) for i, port in enumerate(ports)]

    nodes[0].send_message("Hello from Node 0", ports[1])  # Send message to Node 1
    nodes[1].send_message("Hello from Node 1", ports[0])  # Send message to Node 0
    nodes[0].broadcast_message("Hey all, I'm Node Zero!")
    
    # Ensure all nodes are closed properly
    for node in nodes:
        node.close()