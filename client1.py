import socket
import threading

class UDPNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', 0))  # Let OS assign an available port
        self.port = self.sock.getsockname()[1]  # Get the assigned port
        self.address = ('localhost', self.port)
        print(f"Node {self.node_id} bound to port {self.port}")

        # Start listening thread
        self.listener_thread = threading.Thread(target=self.listen)
        self.listener_thread.start()

    def listen(self):
        while True:
            data, addr = self.sock.recvfrom(1024)  # Buffer size is 1024 bytes
            print(f"Node {self.node_id} received message: {data.decode()} from {addr}")

    def send_message(self, message, recipient_port):
        self.sock.sendto(message.encode(), ('localhost', recipient_port))
        print(f"Node {self.node_id} sent message: {message} to port {recipient_port}")

    def close(self):
        self.sock.close()
        print(f"Node {self.node_id} closed socket")

if __name__ == "__main__":
    nodes = [UDPNode(node_id=i) for i in range(10)]
    # Example usage: Sending messages between nodes
    nodes[0].send_message("Hello from Node 0", nodes[1].port)  # Send message to Node 1
    nodes[1].send_message("Hello from Node 1", nodes[0].port)  # Send message to Node 0