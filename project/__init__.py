from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'AAAAAA123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)

    with app.app_context():
        db.create_all()

    from . import main, auth
    app.add_url_rule('/', view_func=main.index)
    app.add_url_rule('/profile', view_func=main.profile)
    app.add_url_rule('/login', view_func=auth.login, methods=['GET'])
    app.add_url_rule('/login',view_func=auth.login_post, methods=['POST'])
    app.add_url_rule('/register',view_func=auth.register, methods=['GET'])
    app.add_url_rule('/register',view_func=auth.register_post, methods=['POST'])
    app.add_url_rule('/logout',view_func=auth.logout, methods=['GET', 'POST'])

    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app