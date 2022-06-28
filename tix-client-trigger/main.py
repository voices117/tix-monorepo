import logging
import os
from server import Server


HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', '7561'))
LOG_LEVEL = os.environ.get('LOG_LEVEL', logging.INFO)
WORKER_POOL_SIZE = int(os.environ.get('WORKER_POOL_SIZE', '10'))
CLIENT_EXPIRATION_SECONDS = int(os.environ.get('CLIENT_EXPIRATION_SECONDS', '120'))


if __name__ == '__main__':
    logging.basicConfig(level=LOG_LEVEL)

    server = Server(
        listen_address=(HOST, PORT),
        pool_size=WORKER_POOL_SIZE,
        client_expiration_seconds=CLIENT_EXPIRATION_SECONDS,
    )

    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
