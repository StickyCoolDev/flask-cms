import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_htmx import HTMX
from flask_moment import Moment

# Remove the import line 'from app import db'

from config import Config

# db object is created here and is accessible within this file.
db = SQLAlchemy()
migrate = Migrate()
htmx = HTMX()
moment = Moment()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'please log in to access this page'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    ##Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    htmx.init_app(app)
    login.init_app(app)
    moment.init_app(app)

    from app.models import User
    @login.user_loader
    def load_user(id):
        return db.session.get(User, int(id))

    ##Blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.widgets import bp as widget_bp
    app.register_blueprint(widget_bp, url_prefix='/widgets')

    from app.cli import bp as cli_bp
    app.register_blueprint(cli_bp)
    from app.auth.routes import bp as login_bp
    app.register_blueprint(login_bp)

    ##Logging
    if not app.debug and not app.testing:
        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/flask_cms.log',
                                               maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('CMS startup')

    return app

#from app import models
