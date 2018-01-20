# coding=utf-8
from flask import Blueprint

mobile = Blueprint('mobile', __name__)

from app.main import views
