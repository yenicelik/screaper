"""
    Get orders for a certain user
"""
from dotenv import load_dotenv

from screaper_backend.resources.database import screaper_database

load_dotenv()


class Parts:

    def __init__(self):
        self._parts = screaper_database.read_parts()
        print("self parts are: ", self._parts)

    def parts(self):
        return set(self._parts)


model_parts = Parts()
