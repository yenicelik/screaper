"""
    Runner script for the application
"""
from screaper_language_model.application.application import application

if __name__ == "__main__":
    print("Starting engine")
    application.run(debug=True, processes=1, use_reloader=False, threaded=False)
