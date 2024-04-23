from project.blueprints.models import User, Follow
from project.utils import user_utils

import random

def generate_users(app, db):
    for i in range(50):
            user_utils.add_user("GENERATED_USER_" + str(i), "123")
    db.session.commit()

def get_random_user(db):
      return random.choice(db.session.query(User))