# run the application hosted as a package in app folder
from app import app
# push shell context processor
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from app.models import User, Post


@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Post': Post}
