import time
import threading
from queue import Queue

class Server:
    def __init__(self, env, server_id, enable_debug = False):
        self.env = env
        self._accepting_request = True
        self._enable_debug = enable_debug
        self.processing_time = 0
        self.queue = Queue()
        self.requests_received = 0
        self.requests_processed = 0
        self.server_id = server_id
        self.state = 'AWAY'

        # Faz com que process_request seja incluido no ambiente de simulacao (nao tenho certeza)
        self.action = env.process(self.process_request())

    def process_request(self):
        while True:
            if not self.queue.empty():
                self.state = 'RUNNING'
                request = self.queue.get()

                processing_time = request["cpu_time"] + request["io_time"]
                self.processing_time += processing_time

                if self._enable_debug:
                    print(f"Servidor {self.server_id} processando requisição {request['id']} ({processing_time}s)")

                yield self.env.timeout(processing_time)
                self.queue.task_done()
                self.requests_processed += 1
                if self._enable_debug:
                    print(f"Servidor {self.server_id} finalizou a requisição {request['id']}")
            else: 
                self.state = 'AWAY'
                yield self.env.timeout(0.1)


    def stop(self):
        self._accepting_request = False

    def print_metrics(self):
        avg_response_time = self.processing_time / self.requests_processed if self.requests_processed > 0 else 0

        # TODO nao sei se as metricas sao em relacao as requisicoes que foram recebidas ou so em relacao as que foram realmente processadas
        print(f"===== Metrics for Server {self.server_id} =====")
        print(f"Requests received: {self.requests_received}")
        print(f"Requests processed: {self.requests_processed}")
        print(f"Estado do servidor: {self.state}")
        print(f"Accumulated processing time: {self.processing_time}")
        print(f"Average response time: {avg_response_time}")
        print("================================\n")
        pass
