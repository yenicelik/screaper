"""
    Running the flask application
"""
from os import environ
from screaper_backend.application.application import application

if __name__ == "__main__":
    print("Starting flask application ")
    application.run(port=environ.get("PORT"), debug=True)
