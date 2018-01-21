import os
from base64 import b64encode
import numpy as np
from sklearn import neighbors
import random
import pickle
import numpy as np

from flask import request, jsonify, redirect, url_for, current_app
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
    # auth_token = request.headers.get('Authorization')
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
    tags = cloud_api.test_request(image_path)
    print(tags)
    for tag in tags:
        t = Tag(name=tag, garment_id=garment.id)
        db.session.add(t)

    db.session.commit()

    return jsonify({"image_path": image_path})


@mobile.route('/trending')
def trending():
    img = []
    link = []

    img.append("https://images-na.ssl-images-amazon.com/images/I/51KlaoGaVKL._AC_UL260_SR200,260_.jpg")
    link.append(
        "https://www.amazon.com/Trend-Womens-Paris-Bohemian-Sleeve/dp/B011SP0IUC/ref=sr_1_1?s=apparel&ie=UTF8&qid=1516488999&sr=1-1&nodeID=7141123011&psd=1")

    img.append("https://images-na.ssl-images-amazon.com/images/I/410z-V3xCzL._AC_UL260_SR200,260_.jpg")
    link.append(
        "https://www.amazon.com/Trend-Sleeve-Casual-Cocktail-Floral/dp/B01N1A38VG/ref=sr_1_2?s=apparel&ie=UTF8&qid=1516488999&sr=1-2&nodeID=7141123011&psd=1")

    img.append("https://images-na.ssl-images-amazon.com/images/I/51T1sApy%2BhL._AC_UL260_SR200,260_.jpg")
    link.append(
        "https://www.amazon.com/Trend-Womens-Sleeve-V-Neck-Bohemian/dp/B073XV9572/ref=sr_1_3?s=apparel&ie=UTF8&qid=1516488999&sr=1-3&nodeID=7141123011&psd=1")

    img.append("https://images-na.ssl-images-amazon.com/images/I/41rANSPOK0L._AC_UL260_SR200,260_.jpg")
    link.append(
        "https://www.amazon.com/Trend-Sleeve-V-Neck-Floral-Bohemian/dp/B074KNRQDF/ref=sr_1_4?s=apparel&ie=UTF8&qid=1516488999&sr=1-4&nodeID=7141123011&psd=1")

    img.append("https://images-na.ssl-images-amazon.com/images/I/51X6nOtmCVL._AC_UL260_SR200,260_.jpg")
    link.append(
        "https://www.amazon.com/Trend-Paris-Bohemian-Sleeve-Floral/dp/B074KNLD4H/ref=sr_1_5?s=apparel&ie=UTF8&qid=1516488999&sr=1-5&nodeID=7141123011&psd=1")

    img.append("https://images-na.ssl-images-amazon.com/images/I/41sM7hiTKNL._AC_UL260_SR200,260_.jpg")
    link.append(
        "https://www.amazon.com/Trend-Paris-Short-Sleeve-Dress/dp/B06Y1TCXBD/ref=sr_1_6?s=apparel&ie=UTF8&qid=1516488999&sr=1-6&nodeID=7141123011&psd=1")

    img.append("https://images-na.ssl-images-amazon.com/images/I/417XYNm-5qL._AC_UL260_SR200,260_.jpg")
    link.append(
        "https://www.amazon.com/Trend-Paris-Floral-Bohemian-Sleeve/dp/B00JHQKJQ8/ref=sr_1_7?s=apparel&ie=UTF8&qid=1516488999&sr=1-7&nodeID=7141123011&psd=1")

    img.append("https://images-na.ssl-images-amazon.com/images/I/41iLLezChpL._AC_UL260_SR200,260_.jpg")
    link.append(
        "https://www.amazon.com/Trend-Seasons-Change-Sleeve-Damask/dp/B00FH7C5UY/ref=sr_1_8?s=apparel&ie=UTF8&qid=1516488999&sr=1-8&nodeID=7141123011&psd=1")

    img.append("https://images-na.ssl-images-amazon.com/images/I/414V6Z0HGEL._AC_UL260_SR200,260_.jpg")
    link.append(
        "https://www.amazon.com/Trend-Paris-Bohemian-Sleeve-Short/dp/B013S1XKRW/ref=sr_1_9?s=apparel&ie=UTF8&qid=1516488999&sr=1-9&nodeID=7141123011&psd=1")

    img.append("https://images-na.ssl-images-amazon.com/images/I/41bEIOo-9XL._AC_UL260_SR200,260_.jpg")
    link.append(
        "https://www.amazon.com/Trend-Womens-Sleeve-T-Shirt-Contrast/dp/B00GXI1CIW/ref=sr_1_10?s=apparel&ie=UTF8&qid=1516488999&sr=1-10&nodeID=7141123011&psd=1")

    img.append("https://images-na.ssl-images-amazon.com/images/I/514lz7VXTSL._AC_UL260_SR200,260_.jpg")
    link.append(
        "https://www.amazon.com/Trend-Bohemian-Print-Sleeveless-Floral/dp/B072BBH62F/ref=sr_1_11?s=apparel&ie=UTF8&qid=1516488999&sr=1-11&nodeID=7141123011&psd=1")

    img.append("https://images-na.ssl-images-amazon.com/images/I/51c3lf%2BaIZL._AC_UL260_SR200,260_.jpg")
    link.append(
        "https://www.amazon.com/Trend-Bohemian-Print-Retro-Multicolor/dp/B01BS92BJ4/ref=sr_1_12?s=apparel&ie=UTF8&qid=1516488999&sr=1-12&nodeID=7141123011&psd=1")

    img.append("https://images-na.ssl-images-amazon.com/images/I/41inu9IkOEL._AC_UL260_SR200,260_.jpg")
    link.append(
        "https://www.amazon.com/Womens-Trend-Sleeveless-Halter-Medium/dp/B01BPU3I2U/ref=sr_1_15?s=apparel&ie=UTF8&qid=1516488999&sr=1-15&nodeID=7141123011&psd=1")

    img.append("https://images-na.ssl-images-amazon.com/images/I/31YaJuM04TL._AC_UL260_SR200,260_.jpg")
    link.append(
        "https://www.amazon.com/IZOD-Little-Toddler-Sleeve-Oxford/dp/B00APDFJP8/ref=lp_3002596011_1_1?s=apparel&ie=UTF8&qid=1516492655&sr=1-1&nodeID=3002596011&psd=1")

    img.append("https://images-na.ssl-images-amazon.com/images/I/41ACx4mOpaL._AC_UL260_SR200,260_.jpg")
    link.append(
        "https://www.amazon.com/s/ref=lp_3002596011_blf_1_5?fst=fsl%3AMarvel&rh=i%3Afashion%2Cn%3A3002596011%2Cp_89%3AMarvel&ie=UTF8&qid=1516492655")

    img.append("https://images-na.ssl-images-amazon.com/images/I/91MvLKs2bLL._AC_SR201,266_.jpg")
    link.append(
        "https://www.amazon.com/gp/product/B00JULWEAE/ref=s9_acsd_top_hd_bw_b4Mio_c_x_3_w?pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-5&pf_rd_r=5J1Q7MVAEVFF2TMC4PKY&pf_rd_t=101&pf_rd_p=8a8f09ed-5cb5-5dc6-8bb3-60e637fbcb91&pf_rd_i=1040658")

    return jsonify({img, link})


@mobile.route('/rec', methods=["POST", "GET"])
def rec():
    # Features: type, color, season/weather, day
    # Type: Shirt, Pants, Hat, Socks, Shoes, Boots, Shorts
    # Color: red, Green, blue, yellow, orange, purple, indigo
    # Season: Winter, Spring, Summer, Fall
    # Day: Sunday, Monday, Tues, Wed, Thu, Fri, Sat

    # tags is list of lists

    tags = Tag.query.all()
    y = []
    for i in tags:
        y.append(random.randint(1, 100))

    # print(len(tags))
    # Assign ranks to various clothing articles

    model = neighbors.KNeighborsRegressor()
    model.fit(np.array(tags), np.array(y))
    pickle.dump(model, os.getcwd() + 'recommender')

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
