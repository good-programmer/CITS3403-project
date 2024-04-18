from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import DEBUG, PORT, SECRETKEY

from .blueprints.main import main
from .blueprints.auth import auth

from .utils import route_utils as route

def create_app():
    app = Flask(__name__)
    app.secret_key = SECRETKEY
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{app.root_path}/db/users.db"

    from .blueprints.models import db
    db.init_app(app)

    with app.app_context():
        db.create_all()
    
    app.register_blueprint(main)
    app.register_blueprint(auth)

    from .blueprints.models import User
    login_manager = LoginManager()
    login_manager.login_view = route.login
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

app = create_app()