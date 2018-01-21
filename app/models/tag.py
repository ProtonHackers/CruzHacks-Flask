# coding=utf-8

from app import db

class Tag(db.Model):
    __table_name__ = 'Tag'
    extend_existing = True
    tag_id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(100))
    garment_id = db.Column(db.Integer, db.ForeignKey('garment.id'))

    def __repr__(self):
        return '<Tag {}>'.format(self.name)
