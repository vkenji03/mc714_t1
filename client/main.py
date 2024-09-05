import socket
import struct
import random
import threading
import time

from load_balancer.main import LoadBalancer
from server.main import Server

SERVERS_ADDR = [('127.0.0.1', 8080), ('127.0.0.1', 8081), ('127.0.0.1', 8082)]
LOADBALANCER_ADDR = ('127.0.0.1', 8083)

def requisition(host, port, time):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(struct.pack('i', time))
        data = s.recv(1024)
        print(f'Recebido: {data}')

def do_requests():
    for _ in range(3):
        host, port = LOADBALANCER_ADDR
        for _ in range(random.randint(1, 5)):
            t = threading.Thread(target=requisition, args=(host, port, random.randint(1, 5)))
            t.daemon = True
            t.start()
        time.sleep(random.randint(1, 3))

def main():
    servers = []

    for i, server_info in enumerate(SERVERS_ADDR):
        host, port = server_info
        server = Server(host, port, i)
        servers.append(server)

        # Start server listening on another thread
        t = threading.Thread(target=server.create)
        t.daemon = True
        t.start()

    lb = LoadBalancer(LOADBALANCER_ADDR[0], LOADBALANCER_ADDR[1], servers, 'random')
    t = threading.Thread(target=lb.create)
    t.daemon = True
    t.start()

    time.sleep(2)

    do_requests()

    for server in servers:
        server.stop()

main()