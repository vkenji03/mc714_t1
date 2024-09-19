import random
from queue import Queue

class LoadBalancer:
    def __init__(self, servers, mode="random", enable_debug = False):
        self._current_server = 0
        self._enable_debug = enable_debug
        self._mode = mode
        self._servers = servers


    def balance_request(self, request):
        if self._mode == "random":
            self.random_policy(request)
        elif self._mode == "round_robin":
            self.round_robin_policy(request)
        elif self._mode == "shortest_queue":
            self.shortest_queue_policy(request)

    def random_policy(self, request):
        server = random.choice(self._servers)
        server.queue.put(request)
        server.requests_received += 1

        if self._enable_debug:
            print(f"Requisição eviada ao servidor {server.server_id}")

    def round_robin_policy(self, request):
        server = self._servers[self._current_server]
        self._current_server = (self._current_server + 1) % len(self._servers)
        server.queue.put(request)
        server.requests_received += 1

        if self._enable_debug:
            print(f"Requisição eviada ao servidor {server.server_id}")

    def shortest_queue_policy(self, request):
        server = min(self._servers, key=lambda s: s.queue.qsize())
        server.queue.put(request)
        server.requests_received += 1

        if self._enable_debug:
            print(f"Requisição eviada ao servidor {server.server_id}")
