import socket
import threading

class UDPNode:
    def __init__(self, node_id, port):
        self.node_id = node_id
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', self.port))
        self.address = ('localhost', self.port)
        print(f"Node {self.node_id} bound to port {self.port}")

        # Start listening thread
        self.listener_thread = threading.Thread(target=self.listen)
        self.listener_thread.start()

    def listen(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)  # Buffer size is 1024 bytes
                print(f"Node {self.node_id} received message: {data.decode()} from {addr}")
            except Exception as e:
                print(f"Node {self.node_id} encountered an error: {e}")
                break

    # Send private message
    def send_message(self, message, recipient_port):
        self.sock.sendto(message.encode(), ('localhost', recipient_port))
        print(f"Node {self.node_id} sent message: {message} to port {recipient_port}")

    # Broadcast message
    def broadcast_message(self, message):
        for port in range(13000, 13010):
            if port != self.port:
                self.sock.sendto(message.encode(), ('localhost', port))
        print(f"Node {self.node_id} broadcasted message: {message}")

    def close(self):
        self.sock.close()
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