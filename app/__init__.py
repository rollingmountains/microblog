# Application is hosted as a package
from flask import Flask
from config import Config  # import Config class from config file
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# set the instance of the app
app = Flask(__name__)

# load env variables
load_dotenv()

# set the app configs using env variables
app.config.from_object(Config)

# instance of sqlalchemy
# the instance variable acts as bridge between flask app and database
# db variable access the config file for the SQLALCHEMY_DATABASE_URI variable to connect to db
# db instance variable provides db.session, db.Model, db.metadata etc
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# login manager instance
login = LoginManager(app)
login.login_view = 'login'


# registering the routes in function to stop imports to move to top upon save


def register_routes():
    from app import routes, models


register_routes()
