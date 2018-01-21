import os
from base64 import b64encode
import cv2
import numpy as np
from sklearn import neighbors
import random
import pickle
import numpy as np
from app.mobile import backgrounds
from pytrends.request import TrendReq
from PIL import Image

from flask import request, jsonify, redirect, url_for, current_app, send_from_directory
from google.auth.transport import requests
from google.oauth2 import id_token

from app import db
from app.mobile import mobile
from app.models.user import User
from app.models.garment import Garment
from app.models.tag import Tag
from app.main.utils import save_files
from app.vision import cloud_api

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


def create_user(user):
    """
    Commits a User to the Database. If there is an error, then returns None.
    :param user: a new user
    :return: The created user or None
    """
    try:
        db.session.add(user)
        db.session.commit()
        print("Created User")
        return user
    except Exception as e:
        print(e)
        return None


@mobile.route('/google_login', methods=["POST", "GET"])
def mobile_google_login():
    print(request.data)
    data = get_decoded_data(request.data)
    google_id_token = data.get('googleIdToken')
    email = data.get('email')
    full_name = data.get('full_name')
    # import requests
    result = os.popen("curl https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={}".format(google_id_token)).read()
    import json
    user_id = json.loads(result).get('sub')
    # user_id = requests.get('https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={}'.format(google_id_token)).json().get('sub')
    if user_id is None:
        return jsonify({"error": "Incorrect Google Login Token. Please Try Again"}), 401
    user = User.query.filter_by(google_id_token=user_id).first()
    if user is None:
        user = User(username=email, email=email, full_name=full_name, google_id_token=user_id, email_verified=1)
        create_user(user)
    access_token = generate_access_token()
    user.mobile_access_token = access_token
    db.session.commit()
    print("Created Google User")
    return jsonify({"accessToken": access_token, "message": "Google Login Correct", "userID": user.user_id})


@mobile.route('/upload', methods=["POST", "GET"])
def mobile_file_upload():
    print(request.files, request.data, request.json)
    auth_token = request.form.get("Authorization")
    if auth_token is None:
        return jsonify({"error": "Invalid Auth Token. Please Sign in again"}), 403
    user = User.query.filter_by(mobile_access_token=auth_token).first()
    if user is None:
        return jsonify({"error": "Invalid Token."}), 403
    image_path, _ = save_files('image_file', current_app.config['UPLOAD_TEMPLATE'], request.files)
    garment = Garment(user_id=user.user_id, img_url=image_path)
    db.session.add(garment)
    db.session.commit()
    backgrounds.remove_background(image_path)

    tags = cloud_api.test_request(image_path)
    print(tags)
    for tag in tags:
        t = Tag(name=tag, garment_id=garment.id)
        db.session.add(t)

    db.session.commit()

    return jsonify({"image_path": image_path, "tags": tags})


@mobile.route('/trending', methods=['POST', 'GET'])
def trending():
    pytrends = TrendReq(hl='en-US', tz=360)
    prev_list = []
    terms = []

    tags = Tag.query.all()
    for i in range(5):
        if not tags[i].name in prev_list:

            pytrends.build_payload([tags[i].name], cat=0, timeframe='today 5-y', geo='', gprop='')
            popular_search_terms \
                = pytrends.related_queries()[u'{}'.format(tags[i].name)][u'rising'].values.T[0]
            terms += popular_search_terms

    return jsonify(terms)


@mobile.route('/rec', methods=["POST", "GET"])
def rec():
    # Features: type, color, season/weather, day
    # Type: Shirt, Pants, Hat, Socks, Shoes, Boots, Shorts
    # Color: red, Green, blue, yellow, orange, purple, indigo
    # Season: Winter, Spring, Summer, Fall
    # Day: Sunday, Monday, Tues, Wed, Thu, Fri, Sat

    # tags is list of lists

    tags = Tag.query.all()
    X = []
    y = []
    attrs = []
    counter = []
    recommend = []
    for i in tags:
        if i.name not in attrs:
            attrs.append(i)
            counter.append(1)
        else:
            idx = attrs.index(i.name)
            counter[idx] += 1

    max_idx = counter.index(max((counter)))
    recommend.append(attrs[max_idx])
    del attrs[max_idx]
    del counter[max_idx]

    max_idx = counter.index(max((counter)))
    recommend.append(attrs[max_idx])
    del attrs[max_idx]
    del counter[max_idx]

    max_idx = counter.index(max((counter)))
    recommend.append(attrs[max_idx])
    del attrs[max_idx]
    del counter[max_idx]

    max_idx = counter.index(max((counter)))
    recommend.append(attrs[max_idx])
    del attrs[max_idx]
    del counter[max_idx]

    max_idx = counter.index(max((counter)))
    recommend.append(attrs[max_idx])
    del attrs[max_idx]
    del counter[max_idx]

    max_idx = counter.index(max((counter)))
    recommend.append(attrs[max_idx])
    del attrs[max_idx]
    del counter[max_idx]

    max_idx = counter.index(max((counter)))
    recommend.append(attrs[max_idx])
    del attrs[max_idx]
    del counter[max_idx]

    # print(len(tags))
    # Assign ranks to various clothing articles

    model = neighbors.KNeighborsRegressor()
    model.fit(np.array(tags), np.array(y))
    pickle.dump(model, os.getcwd() + 'recommender')

    url = []
    for i in recommend:
        g = Garment.query.filter_by(i.garment_id).first()

        url.append([Image.open(g.img_url), g.img_url, i])

    return url


@mobile.route('/sync', methods=['POST', 'GET'])
def sync():
    img = []
    img.append(
        "http://www.prana.com/media/catalog/product/cache/1/image/2000x/040ec09b1e35df139433887a97daa66f/w/3/w3amel116_black_l_alt_9.jpg")
    img.append("https://xo.lulus.com/images/product/xlarge/2341622_369362.jpg")
    img.append("http://www.boerandfitch.com/14968-thickbox_default/zebra-print-womens-top.jpg")
    img.append("https://assets.academy.com/mgen/95/10787095.jpg")
    img.append("https://images-na.ssl-images-amazon.com/images/I/717Z-BZnW3L._UX385_.jpg")
    img.append(
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTwXiGr6w-Dm1HSf6bgJkBbmvrJziIwr1wqSdjQSDgHUiW4rcPLQw")

    return jsonify(img)


@mobile.route('/get_image/<string:path>')
def get_image(path):
    return send_from_directory(current_app.config["UPLOAD_TEMPLATE"],
                               filename=path,
                               as_attachment=True)

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
