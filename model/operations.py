from peewee import *
from models import *


def create_table():
    try:
        dbhandle.connect()
        Request.create_table()
    except InternalError as px:
        print(str(px))


if __name__ == '__main__':
    create_table()