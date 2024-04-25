from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

from .config import Config

from .utils import route_utils as route

db = SQLAlchemy()
migrate = Migrate(directory=Config.MIGRATION_DIR)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()
    
    from .blueprints.main import main
    from .blueprints.auth import auth
    from .blueprints.game import game
    
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(game)

    from .blueprints.models import User
    login_manager = LoginManager()
    login_manager.login_view = route.login
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

app = create_app()