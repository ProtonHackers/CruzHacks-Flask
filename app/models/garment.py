# coding=utf-8

from app import db


class Garment(db.model):
    __table_name__ = 'Garment'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    img_url = db.Column(db.String(350), unique=True)
    user_id = db.Column(db.String(350))
    tags = db.relationship('Tag', backref='garment', lazy='dynamic')

    def __repr__(self):
        return '<Garment {}>'.format(self.garment_id)
