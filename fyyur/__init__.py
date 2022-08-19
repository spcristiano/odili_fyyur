# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

# from sqlalchemy import func
# from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")

db = SQLAlchemy(app)
migrate = Migrate(app, db)
# DONE: connect to a local postgresql database
from fyyur import filters
from fyyur import routes
