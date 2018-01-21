# coding=utf-8

from app import db


class GroupType(object):
    """
    The Group Type to specify user access levels.
    """
    UN_VERIFIED = 0
    APPROVED = 1
    SUPER_ADMIN = 2
    VIEW_ONLY = 3


class User(db.Model):
    """
    Datbase Model for User Object
    """
    __table_name__ = 'User'
    user_id = db.Column(db.Integer, primary_key=True, unique=True)

    username = db.Column(db.String(140), unique=True)
    password = db.Column(db.String(140), unique=False)
    email = db.Column(db.String(140))
    phone = db.Column(db.String(140))
    full_name = db.Column(db.String(140))

    access_level = db.Column(db.Integer, default=GroupType.UN_VERIFIED)
    email_verified = db.Column(db.BOOLEAN)

    email_verification_code = db.Column(db.Text)
    password_reset_code = db.Column(db.Text)
    google_id_token = db.Column(db.Text)
    mobile_access_token = db.Column(db.Text)

    garments = db.relationship('Garment', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def get_row_data(self, style="fields"):
        return self.get_district_contact(style=style)

    def get_district_contact(self, style="fields"):
        if style == "categories":
            return ["Full Name", "Email", "Mobile"]
        return [
            self.full_name,
            self.email,
            self.phone
        ]

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.user_id