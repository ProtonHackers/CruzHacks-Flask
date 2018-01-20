# coding=utf-8
from flask import Blueprint

vision = Blueprint('vision', __name__)

from app.vision import views
