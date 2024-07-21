import socket
import threading
import json
import time
import random

class Node:
    def __init__(self, user_id, address, base_port, total_nodes):
        self.user_id = user_id
        self.address = address
        self.port = base_port + user_id  # Assign different ports to each node
        self.total_nodes = total_nodes
        self.vector_clock = [0] * total_nodes
        self.private_buffers = {i: [] for i in range(total_nodes)}
        self.broadcast_buffer = []

        # Create a UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.address, self.port))

        # Start a thread to listen for incoming messages
        self.listener_thread = threading.Thread(target=self.listen)
        self.listener_thread.start()

        # Start a thread to periodically gossip messages
        self.gossip_thread = threading.Thread(target(self.gossip))
        self.gossip_thread.start()

    def increment_vector_clock(self):
        self.vector_clock[self.user_id] += 1

    def send_broadcast(self, message):
        self.increment_vector_clock()
        broadcast_message = {
            'type': 'broadcast',
            'sender_id': self.user_id,
            'vector_clock': self.vector_clock.copy(),
            'message': message
        }
        self._send_to_all(broadcast_message)

    def send_private(self, recipient_id, message):
        self.increment_vector_clock()
        private_message = {
            'type': 'private',
            'sender_id': self.user_id,
            'recipient_id': recipient_id,
            'vector_clock': self.vector_clock.copy(),
            'message': message
        }
        self._send_to(recipient_id, private_message)

    def _send_to_all(self, message):
        for node_id in range(self.total_nodes):
            if node_id != self.user_id:
                self._send_to(node_id, message)

    def _send_to(self, node_id, message):
        message_data = json.dumps(message).encode('utf-8')
        self.sock.sendto(message_data, (self.address, self.port + node_id))

    def listen(self):
        while True:
            data, _ = self.sock.recvfrom(4096)
            message = json.loads(data.decode('utf-8'))
            self.process_message(message)

    def process_message(self, message):
        if message['type'] == 'broadcast':
            self._process_broadcast(message)
        elif message['type'] == 'private':
            self._process_private(message)

    def _process_broadcast(self, message):
        sender_id = message['sender_id']
        self.vector_clock[sender_id] = max(self.vector_clock[sender_id], message['vector_clock'][sender_id])
        self.broadcast_buffer.append((message['vector_clock'], message))
        self._deliver_broadcasts()

    def _deliver_broadcasts(self):
        self.broadcast_buffer.sort()
        for vc, message in self.broadcast_buffer:
            if self._is_deliverable(vc):
                print(f"Broadcast from {message['sender_id']}: {message['message']}")
                self.vector_clock[message['sender_id']] += 1
                self.broadcast_buffer.remove((vc, message))

    def _is_deliverable(self, vc):
        for i in range(self.total_nodes):
            if i != self.user_id and vc[i] > self.vector_clock[i]:
                return False
        return True

    def _process_private(self, message):
        sender_id = message['sender_id']
        recipient_id = message['recipient_id']
        if recipient_id != self.user_id:
            return  # Ignore if not the intended recipient

        self.vector_clock[sender_id] = max(self.vector_clock[sender_id], message['vector_clock'][sender_id])
        self.private_buffers[sender_id].append((message['vector_clock'], message))
        self._deliver_private(sender_id)

    def _deliver_private(self, sender_id):
        self.private_buffers[sender_id].sort()
        for vc, message in self.private_buffers[sender_id]:
            if self._is_deliverable(vc):
                print(f"Private message from {sender_id}: {message['message']}")
                self.vector_clock[sender_id] += 1
                self.private_buffers[sender_id].remove((vc, message))

    def gossip(self):
        while True:
            time.sleep(random.uniform(0.5, 1.5))  # Random delay between gossip messages
            if self.broadcast_buffer:
                for vc, message in self.broadcast_buffer:
                    self._send_to_all(message)

# Create 10 nodes with different ports
base_port = 12000
nodes = [Node(i, '127.0.0.1', base_port, 10) for i in range(10)]

# Example usage
nodes[0].send_broadcast("Hello, this is a broadcast message.")
nodes[1].send_private(2, "Hello, this is a private message.")