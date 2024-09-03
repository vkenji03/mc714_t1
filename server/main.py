import socket
import queue
import threading
import struct
import time
import sys
import random

SERVERS = [('127.0.0.1', 8080), ('127.0.0.1', 8081), ('127.0.0.1', 8082)]
LOADBALANCER = ('127.0.0.1', 8083)

class Server():
    def __init__(self, host, port, server_num):
        self._queue = queue.Queue()
        self._host = host
        self._port = port
        self._num = server_num

    @property
    def queue(self):
        return self._queue
    
    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port
    
    @property
    def num(self):
        return self._num

    def _handle_request(self):
        while True:
            data, conn = self._queue.get()
            time.sleep(data)
            conn.sendall(f'Response from Server {self._num}'.encode())
            self._queue.task_done()

    def create(self):
        thread = threading.Thread(target=self._handle_request)
        thread.daemon = True
        thread.start()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self._host, self._port))
            s.listen()
            print(f"Server {self._num} listening on {self._host}:{self._port}")

            while True:
                conn, addr = s.accept()
                data = conn.recv(1024)
                data = struct.unpack('i', data)[0]
                self.queue.put([data, conn])
                print(f'Request added on queue of Server {self._num}')

class LoadBalancer():
    def __init__(self, host, port, servers_addr, mode='random'):
        self._host = host
        self._port = port
        self._servers_addr = servers_addr
        self._servers = []
        self._next_server = 0 # attribute only used on mode round_robin
        self._queue = queue.Queue()
        self._modes = {'random': 'random', 'round_robin': 'round_robin', 'shortest_queue': 'shortest_queue'}
        
        try:
            self._mode = self._modes[mode]
        except KeyError:
            sys.exit('Invalid mode chosen for LoadBalancer')


    def _create_servers(self):
        for i, server_info in enumerate(self._servers_addr):
            host, port = server_info
            server = Server(host, port, i)
            self._servers.append(server)
            t = threading.Thread(target=server.create)
            t.start()

        self._num_servers = len(self._servers)

    def _redirect(self, host, port, data, conn):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as redirect_sock:
            redirect_sock.connect((host, port))
            redirect_sock.sendall(data)
            conn.sendall(redirect_sock.recv(1024))
            

    def create(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self._host, self._port))
            s.listen()
            print(f'Load Balancer listening on {self._host}:{self._port}')

            self._create_servers()

            while True:
                conn, addr = s.accept()
                data = conn.recv(1024)
                host, port = None, None

                if (self._mode == 'random'):
                    server = random.randint(0, len(self._servers) - 1)
                    host, port = self._servers_addr[server]
                elif (self._mode == 'round_robin'):
                    host, port = self._servers_addr[self._next_server]
                    self._next_server = (self._next_server + 1) if (self._next_server + 1) < self._num_servers else 0
                else:
                    redirect_server = self._servers[0]
                    for server in self._servers[1:]:
                        if server.queue.qsize() < redirect_server.queue.qsize(): redirect_server = server
                    
                    host, port = redirect_server.host, redirect_server.port

                thread = threading.Thread(target=self._redirect, args=(host, port, data, conn))
                thread.daemon = True
                thread.start()

def main():
    lb = LoadBalancer(LOADBALANCER[0], LOADBALANCER[1], SERVERS, 'shortest_queue')
    t = threading.Thread(target=lb.create)
    t.start()

main()