# coding=utf-8
import io

from google.cloud import vision as cloud_vision
from google.cloud.vision import types as cloud_types


def test_request(image_path):
    image_path = image_path


    client = cloud_vision.ImageAnnotatorClient()

    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = cloud_types.Image(content=content)

    response = client.label_detection(image=image)
    labels = response.label_annotations

    return labels

if __name__ == '__main__':
    test_request()
