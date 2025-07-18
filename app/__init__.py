# Application is hosted as a package
from flask import Flask, request
from config import Config  # import Config class from config file
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
import os
from flask_mail import Mail
from flask_moment import Moment
from flask_babel import Babel

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

# instance of flask mail
mail = Mail(app)

# login manager instance
login = LoginManager(app)
login.login_view = 'login'
login.login_message = "This page is login protected. Please login to access this page"

# flask moment instance
moment = Moment(app)

# flask babel instance


def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])


babel = Babel(app, locale_selector=get_locale)


# log errors via email and in file
if not app.debug:
    # send error emails
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])

        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'],
                subject='Microblog Failure',
                credentials=auth,
                secure=secure
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.handlers = []
            app.logger.addHandler(mail_handler)
            app.logger.setLevel(logging.ERROR)

    # log the errors
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler(
        'logs/microblog.logs', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s: %(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog Server Start')


# registering the routes in function to stop imports to move to top upon save

def register():
    from app import routes, models, errors, mail


register()
