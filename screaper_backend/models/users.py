"""
    Get all customers in the system
"""
from dotenv import load_dotenv

from screaper_backend.resources.database import screaper_database

load_dotenv()


class Users:

    def __init__(self):
        print(f"users initialized")

    def user_by_username(self, username):
        out = screaper_database.read_user_obj(username)
        return out


model_users = Users()
