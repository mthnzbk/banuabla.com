from PIL import Image
from io import BytesIO
import requests
import json


def push_notify(email, title, message, url):
    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Basic ZjNlZGUzMmYtM2ZkNy00Y2U2LWEwNjYtNmNkZjQ4MDhlZjMw"} #rest api code

    payload = {"app_id": "d91ca1dc-1d81-401b-9552-3176ef89bd9d",
               "filters": [
                   {"field": "tag", "key": "eposta", "relation": "=", "value": email}
               ],
               "contents": {"en": message},
               "headings": {"en": title},
               "url": url}

    requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
    # print(req.status_code, req.reason, req.content)


def image_check(image_data):
    try:
        img = Image.open((BytesIO(image_data)))
        return True

    except OSError as err:
        print(err)
        return False


def image_clip(image_path):
    img = Image.open(image_path)
    if img.size[0] < 512:

        if img.size[0] < img.size[1]:
            h_offset = (img.size[1] - img.size[0]) // 2
            box = (0, h_offset, img.size[0], img.size[0]+h_offset)

        if img.size[0] >= img.size[1]:
            w_offset = (img.size[0] - img.size[1]) // 2
            box = (w_offset, 0, img.size[1]+w_offset, img.size[1])

        img.crop(box).save(image_path)

    elif img.size[0] >= 512:
        img = img.resize((512, int((512/img.size[0]) * img.size[1])))

        if img.size[0] < img.size[1]:
            w_offset = (img.size[1] - img.size[0]) // 2
            box = (0, w_offset, img.size[0], img.size[0]+w_offset)

        if img.size[0] >= img.size[1]:
            h_offset = (img.size[0] - img.size[1]) // 2
            box = (h_offset, 0, img.size[1]+h_offset, img.size[1])

        img.crop(box).save(image_path)
