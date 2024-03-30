from flask import Flask
from config import DEBUG, PORT, SECRETKEY
from blueprints.index import bp as index_bp
from blueprints.auth import bp as auth_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = SECRETKEY
    return app

if __name__ == '__main__':
    app = create_app()
    app.register_blueprint(index_bp)
    app.register_blueprint(auth_bp)
    app.run(debug=DEBUG, port=PORT)
