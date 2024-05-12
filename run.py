import os

from project import create_app
from project.config import configurations

flask_config = os.environ.get("FLASK_CONFIG", "default")

app = create_app(configurations[flask_config])