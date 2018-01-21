# coding=utf-8
import requests
import json



def test_request(image_path):

    d = json.dumps({
        "requests":[
            {
      "image":{
        "source":{
          "imageUri":
            "http://46.101.35.228/mobile/get_image/"+image_path
        }
      },
      "features":[
        {
          "type":"LOGO_DETECTION",
          "maxResults":2
        }
                    ]
                    }
                ]
            })
    r = requests.post('https://vision.googleapis.com/v1/images:annotate?key=AIzaSyCq52GDfyXU5TAXGMVpEzvwGyr74XZTF1k', data=d)
    print(r)
    labels = json.loads(r.text)
    print(labels)

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
