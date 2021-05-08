import os

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

# These need to run before further imports, otherwise circular (maybe just put them into __init__
application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE')
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(application)

import screaper_backend.application.application_common
import screaper_backend.application.application_external
import screaper_backend.application.application_internal
