import socket
from threading import Thread
import time


def new_request_process(source_socks, source_address):
    pass

proxy_server_address = ('127.0.0.1', 2999)
proxy_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

proxy_server.bind(proxy_server_address)
proxy_server.listen(5)

while True:

    # jam the listening thread
    socks, address = proxy_server.accept()
    n_thread = Thread(target=new_request_process, args=(socks, address,))
    n_thread.start()
