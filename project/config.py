import os

PORT=5500
DEBUG=True
SECRETKEY='secret'

PATH=os.path.dirname(os.path.abspath(__file__))

class Config:
    TESTING = False #Disables session.commit()
    DEVELOPMENT = True
    DEBUG = True
    SECRET_KEY = 'secret'
    MIGRATION_DIR = f'{PATH}/db/migrations' #Location of database history
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.abspath(os.environ['FLASK_DATABASE_URI']) if "FLASK_DATABASE_URI" in os.environ else f'sqlite:///{PATH}/db/app.db' #Uses test database if set; otherwise 'app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False