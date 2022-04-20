import math
import pyautogui
from PyQt5 import QtCore, QtGui, QtWidgets
import json
import sys
import math
from PIL import ImageGrab
import io
import base64
from threading import Thread


class DataHandler(QtCore.QThread):
    signal = QtCore.pyqtSignal(list)

    def __init__(self, sock, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.socket = sock
        self.partner_ip = '217.173.77.2'
        self.partner_port = 0
        self.command = 'screen'
        self.is_active = False
        self.type = ''
        self.max_bytes = 16384

        self.hot_keys = ['space', 'enter', 'tab']

    def make_handshake(self):
        self.socket.sendto('Hello'.encode('utf-8'), (self.partner_ip, self.partner_port))

    def send_json(self, data):
        try: json_data = json.dumps(data.decode('utf-8'))
        except: json_data = json.dumps(data)

        json_data = 'begin>>' + json_data
        json_data = json_data + '<<end'
        json_data = json_data.encode('utf-8')

        size = len(json_data)

        bytes_sent = 0
        try:
            while bytes_sent < size:
                self.socket.sendto(json_data[bytes_sent:bytes_sent+self.max_bytes], (self.partner_ip, self.partner_port))
                #print(f'sending {json_data[bytes_sent:self.max_bytes]}')
                bytes_sent += self.max_bytes
        except Exception as e:
            print(str(e))

    def receive_json(self):
        last_data = b'Error'
        try:
            total_data = b''
            full_load = False
            while not full_load:
                data, addr = self.socket.recvfrom(self.max_bytes)
                #print(f'received {data}')
                if (b'begin>>' in data) and (b'<<end' in data):
                    data = data.replace(b'begin>>', b'')
                    data = data.replace(b'<<end', b'')
                    total_data += data
                    full_load = True
                elif b'begin>>' in data:
                    data = data.replace(b'begin>>', b'')
                    total_data += data
                elif b'<<end' in data:
                    data = data.replace(b'<<end', b'')
                    total_data += data
                    full_load = True
                else:
                    total_data += data
            last_data = total_data
            return json.loads(total_data.decode('utf-8'))
        except Exception as e:
            print(str(e))
            return json.loads('{}')


class DataHandlerController(DataHandler):
    def run(self):
        while self.is_active:
            response = self.receive_json()
            self.signal.emit([response])
            self.send_json(self.command)
            self.command = 'screen'


class DataHandlerSharer(DataHandler):
    def run(self):
        thread = Thread(target=self.mouse_control)
        thread.start()
        while self.is_active:
            screen = self.screen_handle()
            self.send_json(screen)

    def mouse_control(self):
        while self.is_active:
            response = self.receive_json()
            try:
                response = response.split(' ')
                if 'mouse' in response[0]:
                    self.mouse_active(response[0], response[1], response[2])
                elif 'keyboard' in response[1]:
                    self.keyboard_active(response[0], response[1])
            except Exception as e:
                print(str(e))

    def screen_handle(self):
        buffer = io.BytesIO()
        im = ImageGrab.grab()
        im.save(buffer, format='PNG')
        im.close()
        b64_str = base64.b64encode(buffer.getvalue())
        return b64_str

    def mouse_active(self, mouse_flag, x, y):
        if mouse_flag == 'mouse_left_click':
            pyautogui.leftClick(int(x), int(y))
        elif mouse_flag == 'mouse_right_click':
            pyautogui.rightClick(int(x), int(y))
        elif mouse_flag == 'mouse_double_left_click':
            pyautogui.doubleClick(int(x), int(y))
        elif mouse_flag == 'mouse_scroll':
            pyautogui.scroll(int(y))

    def keyboard_active(self, keyboard_flag, key):
        if keyboard_flag == 'keyboard_button_click':
            if key in self.hot_keys:
                pyautogui.keyDown(key)
            else:
                pyautogui.typewrite(key)
