# coding=utf-8
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from flask.starter_project.app import create_app

socketio = SocketIO(message_queue='redis://')

db = SQLAlchemy()
app = create_app(db_ref=db)
app.app_context().push()