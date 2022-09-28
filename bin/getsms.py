import time
# from bin.1 import getsmscode
import requests
from urllib.parse import urlencode

import requests
import urllib.parse

class getsmscode:
    def req(self, args, endpoint):
        if not endpoint in [1, 2]:
            raise Exception('Endpoint must be 1 or 2.')
        if endpoint == 1:
            return requests.get(self.endpoint1 + urllib.parse.urlencode(args)).text
        elif endpoint == 2:
            return requests.get(self.endpoint2 + urllib.parse.urlencode(args)).text
    
    def __init__(self, username, token):
        self.endpoint1 = 'http://www.getsmscode.com/do.php?'
        self.endpoint2 = 'http://www.getsmscode.com/vndo.php?'
        res = self.req({'action': 'login', 'username': username, 'token': token}, 1)
        if res == 'username is wrong':
            raise Exception(res)
        elif res == 'token is wrong':
            raise Exception(res)
        else:
            self.username = username
            self.token = token
            return None
    
    def get_balance(self):
        res = self.req({'action': 'login', 'username': self.username, 'token': self.token}, 1)
        aargs = res.split('|')
        if not aargs[1]:
            raise Exception(res)
        return aargs[1]
    
    def get_number(self, pid, cocode):
        if cocode == 'cn':
            res = self.req({'action': 'getmobile', 'username': self.username, 'token': self.token, 'pid': pid}, 1)
        else:
            res = self.req({'action': 'getmobile', 'username': self.username, 'token': self.token, 'pid': pid, 'cocode': cocode}, 2)
        if res.isdigit():
            return res
        raise Exception(res)
    
    def get_sms(self,phone_number, cocode,pid='1'):
        url = "http://api.getsmscode.com/usdo.php?"
        payload = {
            "action": "getsms",
            "username": "pay@noborders.net",
            "token": "87269a810f4a59d407d0e0efe58185e6",
            "pid": pid,
            "mobile": phone_number,
            "author": "pay@noborders.net",
            'cocode': cocode
        }
        payload = urlencode(payload)
        full_url = url + payload
        for x in range(10):
            response = requests.post(url=full_url).text
            print(response)
        #     if 'insta' in response:
        #         print(response)
            time.sleep(4)
        # return False
    
    # def get_sms(self, number, pid, cocode):
    #     print(number,pid,cocode)
    #     for _ in range(10):
    #         print(_)
    #         if cocode == 'cn':
    #             res = self.req({'action': 'getsms', 'username': self.username, 'token': self.token, 'pid': pid, 'mobile': number, 'author': self.username}, 1)
    #         else:
    #             res = self.req({'action': 'getsms', 'username': self.username, 'token': self.token, 'pid': pid, 'mobile': number, 'cocode': cocode}, 2)
    #             print(res)
    #             if "Google verification" in res:
    #                 res = res.split(' ')
    #                 for i in res : 
    #                     if i.split('-') :
    #                         i = i.split('—')
    #                         for i_part in i :
    #                             try:
    #                                 if int(i_part):
    #                                     if i_part :
    #                                         return i_part
    #                             except Exception as e : ...
                                
    #         time.sleep(10)
    
    def add_blacklist(self, number, pid, cocode):
        if cocode == 'cn':
            res = self.req({'action': 'addblack', 'username': self.username, 'token': self.token, 'pid': pid, 'mobile': number}, 1)
        else:
            res = self.req({'action': 'addblack', 'username': self.username, 'token': self.token, 'pid': pid, 'mobile': number, 'cocode': cocode}, 2)
        if res == 'Message|Had add black list':
            return True
        return False
    
    







# api = getsmscode('pay@noborders.net','87269a810f4a59d407d0e0efe58185e6')
# a = api.get_number(1,'ml')
# print(a)