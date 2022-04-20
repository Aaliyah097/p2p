from peewee import *
from models import *


def create_table():
    try:
        dbhandle.connect()
        Connection.create_table()
    except InternalError as px:
        print(str(px))


if __name__ == '__main__':
    create_table()