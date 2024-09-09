import time
import threading
from queue import Queue

class Server:
    def __init__(self, server_id, _enable_debug = False):
        self._accepting_request = True
        self._enable_debug = _enable_debug
        self.processing_time = 0
        self.queue = Queue()
        self.requests_received = 0
        self.server_id = server_id
        self.state = 'AWAY'


    def process_request(self):
        self.state = 'RUNNING'
        while self._accepting_request or (not self._accepting_request and not self.queue.empty()):
            if not self.queue.empty():
                request = self.queue.get()
                self.requests_received += 1

                processing_time = request["cpu_time"] + request["io_time"]
                self.processing_time += processing_time

                if self._enable_debug:
                    print(f"Servidor {self.server_id} processando requisição {request['id']} ({processing_time}s)")

                time.sleep(processing_time)
                self.queue.task_done()
                if self._enable_debug:
                    print(f"Servidor {self.server_id} finalizou a requisição {request['id']}")
        self.state = 'AWAY'

    def stop(self):
        self._accepting_request = False

    def print_metrics(self):
        avg_response_time = self.processing_time / self.requests_received if self.requests_received > 0 else 0

        print(f"===== Metrics for Server {self.server_id} =====")
        print(f"Requests received: {self.requests_received}")
        print(f"Accumulated processing time: {self.processing_time}")
        print(f"Average response time: {avg_response_time}")
        print("================================\n")
        pass
