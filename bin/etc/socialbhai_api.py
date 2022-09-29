import requests


ACTION = 'add'
SERVICE_ID = ''
URL = 'https://socialbhai.in/api/v1'
KEY = 'ydwZ40i6Heqv3QtXEW1TTNOZ8V4dOSwI'
VIDEO_LINK = ''
VIEW_QUANTITY = ''
INTERVAL_TIME = 0
parameters = {
    'key' : KEY,
    'action' : ACTION,
    'service' :	SERVICE_ID,
    'link' :	VIDEO_LINK,
    'quantity' : VIEW_QUANTITY,
    'interval' : INTERVAL_TIME
}

r = requests.post(URL,params= parameters)
print(r)
print(r.text)