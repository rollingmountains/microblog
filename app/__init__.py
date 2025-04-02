# Application is hosted as a package
from flask import Flask

app = Flask(__name__)

# registering the routes


def register_routes():
    from app import routes


register_routes()
