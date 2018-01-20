# coding=utf-8
import os
from datetime import datetime
import hashlib
from flask import render_template, g, request, url_for, jsonify
from flask_login import login_required, current_user

from flask import current_app
from app import lm, db
from app.main import main
from app.models.user import User, GroupType


@main.route('/image',methods=["POST","GET"])
def image():
    image_path, _ = save_files('audio_file', current_app.config['UPLOAD_TEMPLATE'], request.files)

    return jsonify({})


def save_files(path, dir, request_files):
    """
    Saves a file uploaded in the form to a certain directory.

    :param path: the uploaded file
    :param dir: the directory to save to
    :param request_files: The request.files taken from the form
    :return: The url, filename or None, None if the file does not exists.
    """
    if path in request_files and request_files[path].filename != "":
        file_url = request.files[path]
        # print("file_url=",file_url)
        secret_file_url = hash_name(file_url.filename + str(datetime.now())) + \
                           os.path.splitext(file_url.filename)[1]
        file_url.save(dir + secret_file_url)
        return secret_file_url, request_files[path].filename
    else:
        return None, None

def hash_name(name):
   """
   A Hashed name with md5
   :param name: the name to hash
   :return: A hashed name
   """
   return hashlib.md5(name.encode('utf-8')).hexdigest()
