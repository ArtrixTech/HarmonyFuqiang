import socket
from threading import Thread
from io import BytesIO
import gzip

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


def unzip_gzip(input_data):
    stream = BytesIO(input_data)
    gzip_obj = gzip.GzipFile(fileobj=stream)
    try:
        return gzip_obj.read()
    except OSError:
        return input_data


def new_request_process(source_socket, source_address):

    def get_port(data):
        try:
            cut_result = cut_string(data, target_host + ":", "/")
            if cut_result.isdigit():
                return int(cut_result)
        except ValueError:
            return 80
        return 80

    def decode(source):
        try:
            return source.decode("gb2312")
        except UnicodeDecodeError:
            try:
                return source.decode("utf-8")
            except UnicodeDecodeError:
                return False

    while True:

        try:
            received = source_socket.recv(1024 * 1024)
        except ConnectionAbortedError:
            break
        except ConnectionResetError:
            break

        if received:

            received = unzip_gzip(received)
            decoded = decode(received)

            if decoded and "CONNECT" not in decoded:

                target_header = decoded.split("\r\n")
                target_host = target_header[1].split(":")[1].strip()
                target_port = get_port(decoded)

                print("Target Host:" + target_host + ":" + str(target_port))

                connect_succeed = False
                target_binder = (target_host, target_port)
                target_socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)

                try:
                    target_socket.connect(target_binder)
                    connect_succeed = True
                except ConnectionRefusedError:
                    target_socket.close()
                    connect_succeed = False
                except socket.gaierror:
                    target_socket.close()
                    connect_succeed = False

                if connect_succeed:

                    target_socket.send(received)
                    target_socket.settimeout(0.5)

                    try:
                        response = target_socket.recv(1024)
                        while response:
                            try:
                                source_socket.send(response)
                                response = target_socket.recv(1024)
                            except ConnectionAbortedError:
                                break

                    except socket.timeout:
                        target_socket.close()
                    except ConnectionAbortedError:
                        target_socket.close()


proxy_server_address = ('127.0.0.1', 2850)
proxy_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

proxy_server.bind(proxy_server_address)
proxy_server.listen(5)

while True:

    # jam the listening thread
    input_socket, address = proxy_server.accept()
    n_thread = Thread(
        target=new_request_process, args=(
            input_socket, address,))
    n_thread.start()
