import socket
import threading
import sys
import random

class LoadBalancer():
    def __init__(self, host, port, servers, mode='random'):
        self._host = host
        self._port = port
        self._servers = servers

        self._next_server = 0 # attribute only used on mode round_robin
        self._modes = {'random': 'random', 'round_robin': 'round_robin', 'shortest_queue': 'shortest_queue'}
        
        try:
            self._mode = self._modes[mode]
        except KeyError:
            sys.exit('Invalid mode chosen for LoadBalancer')

    def _redirect(self, host, port, data, conn):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as redirect_sock:
            redirect_sock.connect((host, port))
            redirect_sock.sendall(data)
            conn.sendall(redirect_sock.recv(3000))

    def _random(self):
        server_index = random.randint(0, len(self._servers) - 1)
        return self._servers[server_index]
    
    def _round_robin(self):
        server = self._servers_addr[self._next_server]
        self._next_server = (self._next_server + 1) if (self._next_server + 1) < self._num_servers else 0 # TODO: use a lib to do this
        return server

    def _shortest_queue(self):
        redirect_server = self._servers[0] # TODO: try to use min function
        for server in self._servers[1:]:
            if server.queue.qsize() < redirect_server.queue.qsize():
                redirect_server = server

        return redirect_server

    def create(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self._host, self._port))
            s.listen()
            print(f'Load Balancer listening on {self._host}: {self._port}')

            while True:
                conn, _ = s.accept()
                data = conn.recv(3000)
                server = None

                if (self._mode == 'random'):
                    server = self._random()
                elif (self._mode == 'round_robin'):
                    server = self._round_robin()
                else:
                    server = self._shortest_queue()

                thread = threading.Thread(target=self._redirect, args=(server.host, server.port, data, conn))
                thread.daemon = True
                thread.start()
