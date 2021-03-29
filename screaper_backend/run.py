"""
    Running the flask application
"""
from os import environ
from screaper_backend.application.application import application

if __name__ == "__main__":
    print("Starting flask application ")
    # port=environ.get("PORT"),
    port = environ.get("PORT")
    print("port is: ", port)
    if port is None:
        application.run(host="0.0.0.0", debug=True, use_reloader=False)
    else:
        application.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)

