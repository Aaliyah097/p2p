import base64
import json
import socket
import os

import peewee
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt

from view.remote_window import Ui_MainWindow as MainWindow
import threading
from threading import Thread
from collections import namedtuple
from json import JSONEncoder
import stun
import time
import uuid
from model.models import *
from model.handler import DataHandler
import pyautogui


class MainControl(QtWidgets.QMainWindow):
	def __init__(self, handler):
		super(MainControl, self).__init__()
		self.ui = MainWindow()
		self.ui.setupUi(self)
		self.window = None

		#self.setAcceptDrops(True)

		#self.showFullScreen()

		self.handler = handler
		self.handler.type = 'recepient'
		print(self.handler.__dict__)

		self.threads = []

		self.handler.make_handshake()

		self.hot_keys = {Qt.Key_Space: 'space', Qt.Key_Escape: 'escape', Qt.Key_Tab: 'tab', Qt.Key_Enter: 'enter'}

		self.handler.is_active = True
		self.handler.signal.connect(self.screen_handler)

		self.handler.start()

	def closeEvent(self, event):
		self.handler.is_active = False
		for thread in self.threads:
			thread.join()
		# self.handler.socket.close()

	def keyReleaseEvent(self, event):
		if event.key() == Qt.Key_Escape:
			self.close()
		super().keyReleaseEvent(event)

	def screen_handler(self, screen_value):
		try:
			decrypt_image = QtCore.QByteArray.fromBase64(screen_value[0].encode('utf-8'))
			image = QtGui.QPixmap()
			if image.loadFromData(decrypt_image, "PNG"):
				#image = image.scaled(3200, 2000)
				self.ui.display_label.setPixmap(image)
				#self.ui.display_label.scaled(3200, 2000)
				#pixmap_rect = self.ui.display_label.rect()
				#scaledPix = self.pixmap.scaled(pyautogui.size(), Qt.KeepAspectRatio, transformMode = Qt.SmoothTransformation)
			else:
				print(decrypt_image)
		except Exception as e:
			pass#print(str(e))

	def keyPressEvent(self, event):

		if event.key() in self.hot_keys:
			mouse_cord = f'keyboard_button_click {self.hot_keys[event.key()]}'
			self.handler.command = mouse_cord
		else:
			mouse_cord = f'keyboard_button_click {event.text()}'
			self.handler.command = mouse_cord

	def event(self, event):
		if event.type() == QtCore.QEvent.MouseButtonPress:
			current_button = event.button()

			if current_button == 1:
				mouse_cord = f'mouse_left_click {event.x()} {event.y()}'
			elif current_button == 2:
				mouse_cord = f'mouse_right_click {event.x()} {event.y()}'
			self.handler.command = mouse_cord

		elif event.type() == QtCore.QEvent.MouseMove:
			mouse_cord = f'mouse_move_to {event.x()} {event.y()}'
			self.handler.command = mouse_cord

		elif event.type() == QtCore.QEvent.MouseButtonDblClick:
			mouse_cord = f'mouse_double_left_click {event.x()} {event.y()}'
			self.handler.command = mouse_cord

		elif event.type() == QtCore.QEvent.Wheel:
			delta = event.angleDelta()
			mouse_cord = f'mouse_scroll {delta.x()} {delta.y()}'
			self.handler.command = mouse_cord

		return QtWidgets.QWidget.event(self, event)
