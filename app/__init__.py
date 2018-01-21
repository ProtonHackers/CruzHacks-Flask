#!/var/www/flask-buzz-web/venv/bin/python
# coding=utf-8

import os

from celery import Celery
from flask import Flask
from flask_jsglue import JSGlue
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from app.config import config, basedir

# from celery import Celery
celery = Celery(__name__,
                broker=os.environ.get('CELERY_BROKER_URL', 'redis://'),
                backend=os.environ.get('CELERY_BROKER_URL', 'redis://'))

db = SQLAlchemy()
migrate = Migrate(render_as_batch=True)
lm = LoginManager()
jsglue = JSGlue()
csrf = CSRFProtect()
mail = Mail()

from app.models.user import *
from app.models.garment import *
from app.models.tag import *


def initialize_celery(app):
    """
    Initialise celery to run with context
    :param app: The app which celery binds too
    :return: Nothing
    """
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask


def create_app(config_name=None, db_ref=None):
    """
    Creates a factory application with all the settings.(Allowing there to be multiple instances.) Also disable csrf for testing.
    Then register blueprints and views.
    :param config_name: The configuration name like Production, development, or testing.
    :param db_ref: Used to celery to run database transactions.
    :return: the factory app.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    if db_ref is None:
        db.init_app(app)
        db.reflect(app=app)
    else:
        db_ref.init_app(app)
        db_ref.reflect(app=app)

    migrate.init_app(app, db)

    app.config['TMP'] = basedir + '/tmp/'

    app.config['UPLOAD_TEMPLATE'] = app.config['TMP'] + "upload/"
    jsglue.init_app(app)
    if config_name != 'testing':
        csrf.init_app(app)

    lm.init_app(app)
    # lm.login_view = 'auth.login'
    lm.session_protection = 'strong'
    app.static_folder = 'static'

    mail.init_app(app)

    app.debug = True

    from app.main import main
    app.register_blueprint(main)

    from app.mobile import mobile as mobile_blueprint
    app.register_blueprint(mobile_blueprint, url_prefix='/mobile')
    csrf.exempt(mobile_blueprint)

    from app.vision import vision as vision_blueprint
    app.register_blueprint(vision_blueprint, url_prefix='/vision')
    csrf.exempt(vision_blueprint)

    celery.conf.update(config[config_name].CELERY_CONFIG)
    initialize_celery(app)

    return app
