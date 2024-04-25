import os

PORT=5500
DEBUG=True
SECRETKEY='secret'

PATH=os.path.dirname(os.path.abspath(__file__))

class Config:
    DEVELOPMENT = True
    DEBUG = True
    SECRET_KEY = 'secret'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{PATH}/db/app.db'