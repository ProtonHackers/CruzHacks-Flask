# coding=utf-8
import json
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """
    Initial Configurations for the Flask App
    """
    CSRF_ENABLED = True
    DEBUG = False
    TESTING = False

    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(db_path)
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:8889/RxCampAssist'

    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    CELERY_CONFIG = {
        'CELERY_BROKER_URL': 'redis://localhost:6379/0',
        'CELERY_RESULT_BACKEND': 'redis://localhost:6379/0',
        'CELERYD_TASK_SOFT_TIME_LIMIT': 120
    }
    SOCKETIO_MESSAGE_QUEUE = 'redis://localhost:6379/0'

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True


class DevelopmentConfig(Config):
    """
    Developmental Configurations
    """
    DEBUG = True
    if os.path.isfile('app/email_config.json'):
        with open('app/email_config.json', 'rb') as f:
            config = json.load(f)
            MAIL_USERNAME = config["email"]
            MAIL_DEFAULT_SENDER = config["email"]  # have to allow less secure apps access
            MAIL_PASSWORD = config["password"]


class ProductionConfig(Config):
    """
    Production Configurations
    """
    if os.path.isfile('app/email_config.json'):
        with open('app/email_config.json', 'rb') as f:
            config = json.load(f)
            MAIL_USERNAME = config["email"]
            MAIL_DEFAULT_SENDER = config["email"]  # have to allow less secure apps access
            MAIL_PASSWORD = config["password"]


class TestingConfig(Config):
    """
    Testing Configurations
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
    CELERY_CONFIG = {'CELERY_ALWAYS_EAGER': True}
    CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
