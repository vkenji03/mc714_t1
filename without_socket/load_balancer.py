import random
from queue import Queue

class LoadBalancer:
    def __init__(self, servers, mode="random"):
        self._servers = servers
        self._mode = mode
        self._current_server = 0

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
        print(f"Requisição {request['id']} atribuída aleatoriamente ao servidor {server.server_id}")

    def round_robin_policy(self, request):
        server = self._servers[self._current_server]
        self._current_server = (self._current_server + 1) % len(self._servers)
        server.queue.put(request)
        print(f"Requisição {request['id']} atribuída ao servidor {server.server_id} via Round Robin")

    def shortest_queue_policy(self, request):
        server = min(self._servers, key=lambda s: s.queue.qsize())
        server.queue.put(request)
        print(f"Requisição {request['id']} atribuída ao servidor {server.server_id} com a fila mais curta")

