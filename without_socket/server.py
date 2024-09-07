import random
import time
import threading
from queue import Queue

class Server:
    def __init__(self, server_id):
        self.server_id = server_id
        self.queue = Queue()
        self._lock = threading.Lock()
        self._accepting_request = True
        
    
    def process_request(self):
        while self._accepting_request:
            if not self.queue.empty():
                request = self.queue.get()
                processing_time = request["cpu_time"] * 2 + request["io_time"] * 5
                print(f"Servidor {self.server_id} processando requisição {request['id']} ({processing_time}s)")
                time.sleep(processing_time)
                self.queue.task_done()
                print(f"Servidor {self.server_id} finalizou a requisição {request['id']}")

    def stop(self):
        self._accepting_request = False
