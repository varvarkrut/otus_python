import socket
import threading
import multiprocessing


class TCPServer:
    def __init__(self, host, port, workers=1):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        self.workers = workers
        print(f"Listening on {self.host}:{self.port}")

    def worker(self, sock):
        while True:
            client_sock, address = sock.accept()
            th = threading.Thread(
                target=self.handle_client_connection, args=(client_sock,)
            )
            th.start()

    def handle_client_connection(self, client_socket):
        raise NotImplementedError

    def serve_forever(self):
        workers_count = self.workers
        while True:
            workers_list = [
                multiprocessing.Process(target=self.worker, args=(self.server,))
                for _ in range(workers_count)
            ]
            for w in workers_list:
                w.start()

            for w in workers_list:
                w.join()
