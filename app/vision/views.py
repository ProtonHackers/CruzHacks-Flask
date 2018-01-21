# coding=utf-8
import os
from datetime import datetime
import hashlib
from flask import request, jsonify

from flask import current_app
from app.vision import vision
from app.vision import cloud_api


@vision.route('/vision', methods=["POST", "GET"])
def vision():
    image_path, _ = save_files('image_file', current_app.config['UPLOAD_TEMPLATE'], request.files)

    labels = cloud_api.test_request(image_path)
    return jsonify({"image_path": image_path})


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
