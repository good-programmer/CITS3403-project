import os
from flask import Flask
import utils.login as login

app = Flask(__name__)


# register the login blueprint
app.register_blueprint(login.bp)

if __name__ == '__main__':
    app.run(debug=True, port=5500)
