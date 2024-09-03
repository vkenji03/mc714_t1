import socket
import struct
import random
import threading
import time

LOADBALANCER = ('127.0.0.1', 8083)

def requisition(host, port, time):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(struct.pack('i', time))
        data = s.recv(1024)
        print(f'Recebido: {data}')

for i in range(5):
    host, port = LOADBALANCER
    for j in range(random.randint(1, 5)):
        t = threading.Thread(target=requisition, args=(host, port, random.randint(1, 5)))
        t.start()
    time.sleep(random.randint(1, 3))