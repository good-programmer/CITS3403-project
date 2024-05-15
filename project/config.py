import os

PORT=5500
DEBUG=True

PATH=os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'default')
    MIGRATION_DIR = f'{PATH}/db/migrations' #Location of database history
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.abspath(os.environ.get('FLASK_DATABASE_URI', f'{PATH}/db/app.db'))

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.abspath(os.environ.get('FLASK_DATABASE_URI', f'{PATH}/db/test.db')) #Use configured database, default: test.db
    

class TestingConfig(DevelopmentConfig):
    COMMITS_DISABLED = False
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.abspath('project/db/:memory:')


configurations = {
    "default": DevelopmentConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}

current_config = None