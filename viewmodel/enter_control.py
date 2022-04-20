import os

import peewee
from PyQt5 import QtWidgets
from view.enter_window import Ui_MainWindow as MainWindow
import urls
from model.models import Account, Connection, dbhandle


class MainControl(QtWidgets.QMainWindow):
	def __init__(self):
		super(MainControl, self).__init__()
		self.ui = MainWindow()
		self.ui.setupUi(self)
		self.window = None

		self.__setup_ui()

	def closeEvent(self, event):
		dbhandle.close()
		event.accept()

	def __setup_ui(self):
		self.ui.enter_button.clicked.connect(lambda: self.enter_account(self.ui.login_input.text(), self.ui.password_input.text()))
		self.ui.error_label.setText('')

		# TODO
		self.ui.login_input.setText('aaliyah')
		self.ui.password_input.setText('aaoem097')

	def enter_account(self, login, password):
		self.ui.error_label.setText('')
		try:
			user = Account.select().where(Account.login == login, Account.password == password).get()
			try:
				conn = Connection.select().where(Connection.user_id == user.id).get()
				conn.is_active = True
				conn.active_peers = 0
				conn.save()
			except peewee.DoesNotExist:
				conn = Connection(user_id=user.id, is_active=True)
				conn.save()

			self.close()
			self.window = urls.path('main/', user=user, connection=conn)
			self.window.show()
		except peewee.DoesNotExist:
			self.ui.error_label.setText('Учетная запись не найдена.')


