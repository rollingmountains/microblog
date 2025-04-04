# Application is hosted as a package
from flask import Flask
from config import Config  # import Config class from config file
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# set the instance of the app
app = Flask(__name__)

# load env variables
load_dotenv()

# set the app configs using env variables
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# registering the routes in function to avoid moving to top upon save


def register_routes():
    from app import routes, models


register_routes()
