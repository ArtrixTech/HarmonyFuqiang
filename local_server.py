import socket
from threading import Thread
import time

IS_DEBUG = False


def cut_string(input_str, head, tail):
    if isinstance(
        head,
        str) and isinstance(
            tail,
            str) and isinstance(
            input_str,
            str):
        try:
            start = input_str.find(head) + len(head)
            end = input_str.find(tail, start)
            rt_str = ""
            for index in range(start, end):
                rt_str += input_str[index]
            return rt_str
        except ValueError as e:
            print("Syntax does not match! Message: " + e)
            raise ValueError("Syntax does not match! Message: " + e)
    else:
        raise TypeError("Inputs are not string!")


def new_request_process(source_socks, source_address):

    while True:

        is_exit = False

        received = None
        try:
            received = source_socks.recv(128 * 1024)
        except OSError:
            pass
        # time.sleep(1)

        if received:
            buf = None
            try:
                buf = received.decode("gb2312")
            except UnicodeDecodeError:
                try:
                    buf = received.decode("utf-8")
                except UnicodeDecodeError:
                    buf = None
                    is_exit = True

            if buf == 'exit' or not buf:
                source_socks.close()
                break

            if buf and "CONNECT" not in buf and not is_exit:

                try:
                    target_header = buf.split("\r\n")
                    target_host = target_header[1].split(":")[1].strip()
                except IndexError:
                    pass

                port = 80
                try:
                    cut_result = cut_string(buf, target_host + ":", "/")
                    if cut_result.isdigit():
                        port = int(cut_result)
                except ValueError:
                    pass
                finally:
                    if IS_DEBUG:
                        print("Thr:" + target_host + "  Port=" + str(port))

                print("Target Host:" + target_host + ":" + str(port))

                connect_succeed = False
                target_host_address = (target_host, port)
                target_socks = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                try:
                    target_socks.connect(target_host_address)
                    connect_succeed = True
                except TimeoutError:
                    try:
                        target_socks.connect(target_host_address)
                        connect_succeed = True
                    except TimeoutError:
                        target_socks.close()
                except ConnectionRefusedError:
                    try:
                        target_socks.connect(target_host_address)
                        connect_succeed = True
                    except ConnectionRefusedError:
                        target_socks.close()
                except socket.gaierror:
                    try:
                        target_socks.connect(target_host_address)
                        connect_succeed = True
                    except socket.gaierror:
                        target_socks.close()

                if connect_succeed:
                    # send the source request
                    target_socks.send(received)

                    # get data for 128bits per batch while the data is still
                    # sending.
                    try:
                        target_socks.settimeout(0.5)
                        data = target_socks.recv(128)
                        while data:
                            source_socks.send(data)
                            data = target_socks.recv(128)
                    except socket.timeout:
                        target_socks.close()
                    except ConnectionAbortedError:
                        target_socks.close()
                    except OSError:
                        target_socks.close()

            else:
                source_socks.close()
                break


proxy_server_address = ('127.0.0.1', 2850)
proxy_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

proxy_server.bind(proxy_server_address)
proxy_server.listen(5)

while True:

    # jam the listening thread
    socks, address = proxy_server.accept()
    n_thread = Thread(target=new_request_process, args=(socks, address,))
    n_thread.start()
