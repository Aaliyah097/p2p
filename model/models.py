from peewee import *
import os
import datetime
from dotenv import load_dotenv
import uuid


load_dotenv()
dbhandle = PostgresqlDatabase(database=os.getenv('db_name'),
                              user=os.getenv('db_user'),
                              password=os.getenv('db_password'),
                              host=os.getenv('db_host'),
                              port=os.getenv('db_port'))


class BaseModel(Model):
    class Meta:
        database = dbhandle


class Account(BaseModel):
    id = PrimaryKeyField(null=False)
    login = CharField(max_length=50)
    password = CharField(max_length=50)
    is_licensed = BooleanField(default=False)
    max_connections = IntegerField(default=1)
    session_timeout = IntegerField(default=15)

    class Meta:
        db_table = 'accounts'
        order_by = ('id',)


class Connection(BaseModel):
    id = PrimaryKeyField(null=False)
    host_ip = CharField(max_length=30, default='')
    host_port = IntegerField(default=0)
    is_active = BooleanField(default=False)
    password = CharField(max_length=8, default=str(uuid.uuid4())[:8])
    active_peers = IntegerField(default=0)
    user_id = ForeignKeyField(Account, to_field='id')
    is_local = BooleanField(default=False)

    class Meta:
        db_table = 'connections'
        order_by = ('id',)


class Request(BaseModel):
    id = PrimaryKeyField(null=False)
    status = CharField(max_length=20, default='awaiting')
    user_id = ForeignKeyField(Account, to_field='id')
    connection_id = ForeignKeyField(Connection, to_field='id')

    class Meta:
        db_table = 'requests'
        order_by = ('id',)

class RequestConnection(BaseModel):
    requests = ForeignKeyField(Request)
    connection = ForeignKeyField(Connection)



