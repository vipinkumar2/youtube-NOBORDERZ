# 601124162826

from urllib.parse import urlencode
import requests, time

def get_sms(phone_number, pid='1',country = 'ml'):
    url = "http://api.getsmscode.com/vndo.php?"
    payload = {
        "action": "getsms",
        "username": "pay@noborders.net",
        "token": "87269a810f4a59d407d0e0efe58185e6",
        "pid": pid,
        "mobile": phone_number,
        "author": "pay@noborders.net",
        "cocode":country
    }
    payload = urlencode(payload)
    full_url = url + payload
    for x in range(10):
        response = requests.post(url=full_url).text
        print(response)
        # if 'insta' in (response).lower():
        #     response = response.split(' ')
        #     otp = response[1]+response[2]
        #     return otp
        time.sleep(4)

    # return False

get_sms('601124162826')
