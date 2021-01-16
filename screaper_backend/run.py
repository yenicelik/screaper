"""
    Running the flask application
"""
from os import environ
from screaper_backend.application.application import application

if __name__ == "__main__":
    print("Starting flask application ")
    # port=environ.get("PORT"),
    application.run(host="0.0.0.0", port=environ.get("PORT"), debug=True)
