import json
import socket
import os

import peewee
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt

from view.main_window import Ui_MainWindow as MainWindow
import threading
from threading import Thread
from collections import namedtuple
from json import JSONEncoder
import stun
import time
import uuid
from model.models import *
import urls
from model.handler import DataHandler, DataHandlerController, DataHandlerSharer


class WorkThread(QtCore.QThread):
	threadSignal = QtCore.pyqtSignal(list)

	def __init__(self, user_id, connection_id, to_port, to_ip, parent=None):
		QtCore.QThread.__init__(self, parent)

		self.user_id = user_id
		self.connection_id = connection_id
		self.to_port = to_port
		self.to_ip = to_ip

	def run(self, *args, **kwargs):
		is_allowed = False
		while not is_allowed:
			try:
				request = Request.select().where(Request.user_id == self.user_id,
												 Request.connection_id == self.connection_id).get()
				request_status = request.status
				if request_status == 'accepted':
					is_allowed = True
					self.threadSignal.emit([self.to_port, self.to_ip])
			except DoesNotExist:
				is_allowed = True


class MainControl(QtWidgets.QMainWindow):
	def __init__(self, user, connection):
		super(MainControl, self).__init__()
		self.ui = MainWindow()
		self.ui.setupUi(self)

		self.user = user
		self.connection = connection

		self.__setup_ui()

		self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.udp_socket.settimeout(0.5)
		self.udp_socket.bind(('', 0))

		self.handler = DataHandler(self.udp_socket)

		self.window = None

		self.threads = []

		self.setup_host()

	def closeEvent(self, event):
		try:
			requests = Request.select().where(Request.user_id == self.user.id)
			for request in requests:
				request.delete_instance()
		except DoesNotExist:
			pass

		self.connection.is_active = False
		self.udp_socket.close()
		for thread in self.threads:
			thread.join()
		dbhandle.close()
		event.accept()

	# отдельный поток для отправки данных о хосте на сервер
	def setup_host(self):
		setup_thread = Thread(target=self.make_host_info)
		self.threads.append(setup_thread)
		setup_thread.start()
		setup_thread.join()

	# отправляет данные о хосте на сервер
	def make_host_info(self):
		status = ''

		try:
			self.udp_socket.sendto(f"request_host_info;{self.connection.id}".encode('utf-8'),
								   (os.getenv('server_host'), int(os.getenv('server_port'))))
			peer_data, addr = self.udp_socket.recvfrom(1024)
			response = peer_data.decode('utf-8').split(';')
			status = response[0]
			self.connection.host_ip = response[1]
			self.connection.host_port = int(response[2])

			if self.connection.is_local:
				s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				s.connect(('8.8.8.8', 80))
				local_ip = s.getsockname()[0]
				self.connection.host_ip = local_ip

				query = Connection.update(host_ip=local_ip).where(Connection.id == self.connection.id)
				query.execute()
		except Exception as e:
			print(str(e))

		if status == 'success':
			self.connection.is_active = True
			self.ui.server_connect_button.hide()
			self.statusBar().showMessage("")
		else:
			self.ui.server_connect_button.show()
			self.statusBar().showMessage(
				"Не удалось соединиться с сервером, нажмите кнопку 'Сессия' для повторной попытки.")

	def __setup_ui(self):
		self.ui.change_password_button.clicked.connect(self.change_connection_password)
		self.ui.myid_input.setText(str(self.user.id))
		self.ui.mypassword_input.setText(self.connection.password)
		self.ui.remote_connect_button.clicked.connect(
			lambda: self.prepare_connect(self.ui.remote_id_input.text(), self.ui.remote_password_input.text()))

		self.ui.refresh_requests_button.clicked.connect(self.load_requests)
		self.load_requests()

		self.ui.server_connect_button.clicked.connect(self.make_host_info)

	def cancel_connect(self, req_id):
		self.connection.is_active = False
		request = Request.select().where(Request.id == req_id).get()
		request.delete_instance()

		self.load_requests()

	def load_requests(self):
		table = self.ui.requests_table
		table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
		table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)

		requests = []
		try:
			requests = Request.select().where((Request.connection_id == self.connection.id) | (Request.user_id == self.user.id))
		except DoesNotExist:
			pass

		table.setRowCount(len(requests))
		row = 0
		for req in requests:
			status = ''
			if int(req.user_id.id) == int(self.user.id):
				if req.status == 'awaiting':
					status = 'Ожидает разрешения'
					btn = QtWidgets.QPushButton(table)
					btn.setText('Отменить')
					btn.setStyleSheet(
						'QPushButton {border-radius: 25px;''background-color: rgb(85, 0, 127);font: 10pt "Calibri";'
						'color: rgb(255, 255, 255); max-width: 160px; max-height: 100px;}'
						'QPushButton:hover {background-color: rgb(133, 0, 200);}'
						'QPushButton:pressed{background-color: rgb(163, 0, 245);};')

					connection = Connection.select().where(Connection.user_id == req.user_id.id).get()
					btn.clicked.connect(lambda: self.cancel_connect(req.id))
					table.setCellWidget(row, 2, btn)
				if req.status == 'accepted':
					status = 'Одобрен'
					btn = QtWidgets.QPushButton(table)
					btn.setText('Удалить')
					btn.setStyleSheet(
						'QPushButton {border-radius: 25px;''background-color: rgb(85, 0, 127);font: 10pt "Calibri";'
						'color: rgb(255, 255, 255); max-width: 160px; max-height: 100px;}'
						'QPushButton:hover {background-color: rgb(133, 0, 200);}'
						'QPushButton:pressed{background-color: rgb(163, 0, 245);};')

					connection = Connection.select().where(Connection.user_id == req.user_id.id).get()
					btn.clicked.connect(lambda: self.cancel_connect(req.id))
					table.setCellWidget(row, 2, btn)
			else:
				if req.status == 'awaiting':
					status = 'Ожидает разрешения'
					btn = QtWidgets.QPushButton(table)
					btn.setText('Удалить')
					btn.setStyleSheet(
						'QPushButton {border-radius: 25px;''background-color: rgb(85, 0, 127);font: 10pt "Calibri";'
						'color: rgb(255, 255, 255); max-width: 160px; max-height: 100px;}'
						'QPushButton:hover {background-color: rgb(133, 0, 200);}'
						'QPushButton:pressed{background-color: rgb(163, 0, 245);};')

					connection = Connection.select().where(Connection.user_id == req.user_id.id).get()
					btn.clicked.connect(lambda: self.allow_connect(connection.host_ip, connection.host_port, req.id))
					table.setCellWidget(row, 2, btn)
				elif req.status == 'accepted':
					status = 'Одобрен'
					btn = QtWidgets.QPushButton(table)
					btn.setText('Удалить')
					btn.setStyleSheet(
						'QPushButton {border-radius: 25px;''background-color: rgb(85, 0, 127);font: 10pt "Calibri";'
						'color: rgb(255, 255, 255); max-width: 160px; max-height: 100px;}'
						'QPushButton:hover {background-color: rgb(133, 0, 200);}'
						'QPushButton:pressed{background-color: rgb(163, 0, 245);};')

					connection = Connection.select().where(Connection.user_id == req.user_id.id).get()
					btn.clicked.connect(lambda: self.cancel_connect(req.id))
					table.setCellWidget(row, 2, btn)

			table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(req.user_id.id)))
			table.setItem(row, 1, QtWidgets.QTableWidgetItem(status))

			row += 1

	def allow_connect(self, from_ip, from_port, req_id):
		request = Request.select().where(Request.id == req_id).get()
		request.status = 'accepted'
		request.save()
		self.load_requests()
		self.ui.statusBar.showMessage('Соединение с {}:{} установлено'.format(from_ip, from_port))
		self.connection.is_active = True

		self.translate(from_ip, from_port)

	def prepare_connect(self, partner_id, partner_password):
		if self.ui.control_type_comboBox.currentText() == 'Удаленное управление':
			thread = Thread(target=self.remote_connect, args=(partner_id, partner_password,))
			self.threads.append(thread)
			thread.start()
		elif self.ui.control_type_comboBox.currentText() == 'Передача файлов':
			pass

	def remote_connect(self, partner_id, partner_password):
		try:
			request = Request.select().where(Request.user_id == self.user.id).get()
			self.ui.statusBar.showMessage("Активное подключение уже имеется. Необходимо прервать его, чтобы создать новое.")
		except DoesNotExist:
			self.ui.statusBar.showMessage("")
			if partner_id != '' and int(partner_id) != self.user.id:
				try:
					partner_connection = Connection.select().where(Connection.user_id == int(partner_id),
																	Connection.password == partner_password).get()
					self.ui.statusBar.showMessage("Запрос на подключение к Пользователю {} отправлен.".format(partner_id))

					request = Request(user_id=self.user.id, connection_id=partner_connection.id, status='awaiting')
					request.save()

					#thread = Thread(target=self.listen, args=(
					# partner_connection.host_ip, partner_connection.host_port, self.user.id, partner_connection.id,))
					# self.threads.append(thread)
					thread = WorkThread(self.user.id, partner_connection.id, partner_connection.host_port, partner_connection.host_ip, parent=self)
					thread.threadSignal.connect(self.listen)
					thread.start()
					self.ui.statusBar.showMessage("Ожидаем ответа от удаленного компьютера, пожалуйста, подождите")
					thread.start()
				except peewee.DoesNotExist:
					self.ui.statusBar.showMessage("Пользователь с ID {} не найден.".format(partner_id))
			else:
				self.ui.statusBar.showMessage("Поле ID Партнера не заполнено или заполнено наверно.")

	def listen(self, data):
		self.connection.is_active = True

		self.handler.partner_ip = data[1]
		self.handler.partner_port = data[0]
		self.ui.statusBar.showMessage('Соединение с {}:{} установлено'.format(data[1], data[0]))
		self.handler = DataHandlerController(self.udp_socket)
		self.handler.is_active = True
		self.handler.partner_port = data[0]

		self.window = urls.path('remote/', handler=self.handler)
		self.window.show()


	def translate(self, from_ip, from_port):
		self.handler = DataHandlerSharer(self.udp_socket)
		self.handler.partner_ip = from_ip
		self.handler.partner_port = from_port
		self.handler.is_active = True
		self.handler.start()

	def change_connection_password(self):
		conn = Connection.select().where(Connection.id == self.connection.id).get()
		conn.password = str(uuid.uuid4())[:8]
		conn.save()
		self.connection.password = conn.password
		self.ui.mypassword_input.setText(self.connection.password)
