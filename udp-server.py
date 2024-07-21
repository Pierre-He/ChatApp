import socket

def start_udp(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('localhost',port))
    print(f'UDP server listening on port {port}')

    while 1:
        message, address = server_socket.recvfrom(1024)
        print(f"Message from {address}: {message.decode()}")


if __name__ == "__main__":
    start_udp(12000)