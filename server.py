import socket
import json
from model.models import *
from threading import Thread
from model.models import Connection
import stun


class Server:
    def __init__(self):
        dbhandle.connect()

        nat_type, external_ip, external_port = stun.get_ip_info()
        print('Server is listening on {}:{} or {}:{}'.format('127.0.0.1', 9090, external_ip, external_port))

        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(('', 9090))

        self.thread = Thread(target=self.listen)
        self.thread.start()

    def listen(self):
        while True:
            data, addr = self.udp_socket.recvfrom(1024)

            response = self.parse_data(data.decode('utf-8'), addr)

            self.udp_socket.sendto(response.encode('utf-8'), addr)

    def parse_data(self, data, addr) -> str:
        response = ''
        print(data)
        request = data.split(";")
        if request[0] == 'request_host_info':
            conn_id = request[1]
            try:
                conn = Connection.select().where(Connection.id == conn_id).get()
                conn.host_ip = addr[0]
                conn.host_port = int(addr[1])
                conn.save()
            except DoesNotExist:
                return 'error;host not found-->not updated'

            response = "success;{};{}".format(addr[0], addr[1])

        return response


server = Server()
