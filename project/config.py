import os

PORT=5500
DEBUG=True
SECRETKEY='secret'

PATH=os.path.dirname(os.path.abspath(__file__))

class Config:
    DEVELOPMENT = True
    DEBUG = True
    SECRET_KEY = 'secret'
    MIGRATION_DIR = f'{PATH}/db/migrations'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.abspath(os.environ['FLASK_DATABASE_URI']) if "FLASK_DATABASE_URI" in os.environ else f'sqlite:///{PATH}/db/app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False