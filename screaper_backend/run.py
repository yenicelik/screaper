"""
    Running the flask application
"""
from screaper_backend.application.application import application

if __name__ == "__main__":
    print("Starting flask application ")
    application.run(debug=True)
