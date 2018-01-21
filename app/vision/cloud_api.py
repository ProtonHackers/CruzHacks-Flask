# coding=utf-8
import io
import requests
import json

from google.cloud import vision as cloud_vision
from google.cloud.vision import types as cloud_types


def test_request(image_path):

    d = {
            "requests":[
                {
                    "image":{
                        "content":image_path
                    },
                "features":[
                    {
                        "type":"LABEL_DETECTION"
                    }
                ]
            }
        ]
    }
    r = requests.post('https://vision.googleapis.com/v1/images:annotate?key=service.json', data=d)
    labels = json.loads(r.text)

    # client = cloud_vision.ImageAnnotatorClient()
    #
    # with io.open(image_path, 'rb') as image_file:
    #     content = image_file.read()
    #
    # image = cloud_types.Image(content=content)
    #
    # response = client.label_detection(image=image)
    # labels = response.label_annotations

    return labels

