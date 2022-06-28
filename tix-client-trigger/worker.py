import time
import socket
import logging

from typing import Tuple
from threading import Lock, Thread


class Worker(Thread):

    def __init__(self, id:int, client_expiration:int, socket:socket.socket) -> None:
        self.id = id
        self.client_expiration = client_expiration
        self.clients = {}
        self.lock = Lock()
        self.stop = False
        self.log = logging.getLogger(f'Worker {self.id}')

        self.socket = socket

        super().__init__()

    def run(self):
        last_client_refresh = time.monotonic()

        while not self.stop:
            start = time.monotonic()
            self.ping_clients()

            if (start - last_client_refresh) > (self.client_expiration / 2):
                self.refresh_clients()
                last_client_refresh = time.monotonic()

            elapsed = time.monotonic() - start

            # sleep until 1 second has elapsed since the previous iteration
            time.sleep(max(0, 1 - elapsed))
        
        self.log.info('stopped')

    def add_client(self, address:Tuple[str, int]):
        self.log.info('add client %s', address)

        with self.lock:
            self.clients[address] = time.monotonic()

        return self.socket.getsockname()

    def ping_clients(self):
        if not self.clients:
            return

        self.log.debug('pinging clients')
        with self.lock:
            for address in self.clients:
                self.socket.sendto(b'\x75\x61', address)

    def refresh_clients(self):
        if not self.clients:
            return

        self.log.debug('refreshing clients list')
        with self.lock:
            remove_list = []

            now = time.monotonic()
            for address, conn_time in self.clients.items():
                if (now - conn_time) > self.client_expiration:
                    self.log.info('client %s expired', address)
                    remove_list.append(address)

            for address in remove_list:
                del self.clients[address]
