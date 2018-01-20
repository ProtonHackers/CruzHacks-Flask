import os
from base64 import b64encode

from flask import request, jsonify, redirect, url_for
from google.auth.transport import requests
from google.oauth2 import id_token

from app import db
from app.mobile import mobile
from app.models.user import User

GOOGLE_CLIENT_ID = "566644882675-2msrrs3402pphinl7lbjpohe80527mak.apps.googleusercontent.com"
from flask import json


def get_decoded_data(data):
    return json.loads(data.decode(encoding='UTF-8'))


def generate_access_token():
    return b64encode(os.urandom(20)).decode('utf-8')


@mobile.route('/login', methods=["POST", "GET"])
def mobile_login():
    data = get_decoded_data(request.data)
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username, password=password).first()
    if user is not None:
        if not user.email_verified:
            return jsonify({"error": "Check Ur email to Verify Your Account"}), 401  # Invalid Username
        access_token = generate_access_token()
        user.mobile_access_token = access_token
        print(access_token)
        db.session.commit()
        return jsonify({"accessToken": access_token, "message": "Login Correct", "userID": user.user_id})  # Correct
    user = User.query.filter_by(username=username).first()
    if user is not None:
        print("Invalid Password")
        return jsonify({"error": "Password Incorrect"}), 401  # Incorrect Password
    return jsonify({"error": "Username Doesn't Exist"}), 401  # Invalid Username


def create_user(user: User):
    """
    Commits a User to the Database. If there is an error, then returns None.
    :param user: a new user
    :return: The created user or None
    """
    try:
        db.session.add(user)
        db.session.commit()
        return user
    except Exception as e:
        print(e)
        return None


@mobile.route('/google_login', methods=["POST", "GET"])
def mobile_google_login():
    print(request.data)
    data = get_decoded_data(request.data)
    print(data)
    google_id_token = data.get('googleIdToken')
    email = data.get('email')
    full_name = data.get('full_name')
    user_id = id_token.verify_oauth2_token(google_id_token, requests.Request(), GOOGLE_CLIENT_ID).get('sub')
    print(user_id)
    if user_id is None:
        return jsonify({"error": "Incorrect Google Login Token. Please Try Again"}), 401

    user = User.query.filter_by(google_id_token=user_id).first()
    if user is None:
        user = User(username=email, email=email, full_name=full_name, google_id_token=user_id, email_verified=1)
        create_user(user)
    access_token = generate_access_token()
    user.mobile_access_token = access_token
    db.session.commit()
    return jsonify({"accessToken": access_token, "message": "Google Login Correct", "userID": user.user_id})


# @mobile.route('/verify_reset_email/<string:update_type>', methods=["POST", "GET"])
# def mobile_verify_reset_email(update_type):
#     if update_type is None:
#         return jsonify({"error": "Invalid Update Type"}), 403
#     data = get_decoded_data(request.data)
#     email = data  # Since only one Item Sent.
#     user = User.query.filter_by(email=email).first()
#     if user is None:
#         return jsonify({"error": "User with Email does not exist. Please Register"}), 401
#     if user.password is None and user.google_id_token is not None:
#         return jsonify({"error": "Google Account does not have a saved Password. Please Reset via Google"}), 403
#
#     send_verify_reset_email(user, update_type=update_type)
#     return jsonify({"message": "Verification Email Sent. "}), 200
