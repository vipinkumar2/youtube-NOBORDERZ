import requests


ACTION = 'add'
SERVICE_ID = '2582'
SERVICE_ID = '2730'
URL = 'https://socialbhai.in/api/v1'
KEY = '5Mu97RS0ezVXUgW2DMbaHJUZaO0gmuTE'
VIDEO_LINK = 'https://www.youtube.com/watch?v=ls6_xV8zKow&ab_channel=DaRTYSTaRK'
VIEW_QUANTITY = '5'
INTERVAL_TIME = 0
parameters = {
    'key' : KEY,
    'action' : ACTION,
    'service' :	SERVICE_ID,
    'link' :	VIDEO_LINK,
    'quantity' : VIEW_QUANTITY,
}

r = requests.post(URL,params= parameters)
print(r)
print(r.text)

# import os
# from dotenv import load_dotenv

# load_dotenv()
# print(os.environ.get("STRIPE_SECRET_KEY"))
# print(os.getenv('URLLL'))
# GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID')
# SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
# STORAGE_BUCKET_NAME = os.getenv('STORAGE_BUCKET_NAME')
# print(GCP_PROJECT_ID)