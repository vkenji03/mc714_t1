import socket
import queue
import threading
import struct
import time

class Server():
    def __init__(self, host, port, server_num):
        self._queue = queue.Queue()
        self._host = host
        self._port = port
        self._num = server_num
        self._stop_thread = threading.Event()

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
        while not self._stop_thread.is_set():
            data, conn = self._queue.get()
            time.sleep(data) # TODO: sleep according to 2 variables
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
                conn, _ = s.accept()
                data = conn.recv(3000)
                data = struct.unpack('i', data)[0]
                self.queue.put([data, conn])
                print(f'Request added on queue of Server {self._num}')

    def stop(self):
        self._stop_thread.set()
