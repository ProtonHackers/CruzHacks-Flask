# coding=utf-8

from app import db

class Garment(db.model):
    __table_name__ = 'Garment'
    garment_id = db.Column(db.Integer, primary_key=True, unique=True)
    garment_name = db.Column(db.String(140), unique=False)
    url = db.Column(db.String(350), unique=True)
