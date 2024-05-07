import os

PORT=5500
DEBUG=True

PATH=os.path.dirname(os.path.abspath(__file__))

class Config:
    TESTING = False #Disables session.commit()
    DEVELOPMENT = True
    DEBUG = True
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'default')
    MIGRATION_DIR = f'{PATH}/db/migrations' #Location of database history
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.abspath(os.environ.get('FLASK_DATABASE_URI', f'{PATH}/db/app.db')) #Uses test database if set; otherwise 'app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False