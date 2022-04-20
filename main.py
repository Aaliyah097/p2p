from PyQt5 import QtWidgets
import sys
import urls
import os
import model
from model import models
import peewee

if __name__ == '__main__':
	models.dbhandle.connect()
	app = QtWidgets.QApplication([])
	application = urls.path('enter/')
	application.show()
	sys.exit(app.exec_())



