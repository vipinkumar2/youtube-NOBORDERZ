import random
from select import select
from urllib.parse import urlencode
from bin.getsms import getsmscode
from driver.driver import get_driver
import time
import csv, requests
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_number(pid='1',country = 'sa'):
    while True:
        url = "http://api.getsmscode.com/vndo.php?"

        payload = {
            "action": "getmobile",
            "username": "pay@noborders.net",
            "token": "87269a810f4a59d407d0e0efe58185e6",
            "pid": pid,
            "cocode":country
        }

        payload = urlencode(payload)
        full_url = url + payload
        response = requests.post(url=full_url)
        response = response.content.decode("utf-8")
        # print(response)
        # time.sleep(1000)
        if str(response) == 'Message|Capture Max mobile numbers,you max is 5':
            continue
        else:break
    return response

def get_sms(phone_number, pid='1',country = 'sa'):
    url = "http://api.getsmscode.com/vndo.php?"
    payload = {
        "action": "getsms",
        "username": "pay@noborders.net",
        "token": "87269a810f4a59d407d0e0efe58185e6",
        "pid": pid,
        "mobile": phone_number,
        "author": "pay@noborders.net",
        # "cocode":country
    }
    payload = urlencode(payload)
    full_url = url + payload
    for x in range(10):
        response = requests.post(url=full_url).text
        print(response)
        res = response
        if "Google verification" in response:
            res = res.split(' ')
            for i in res : 
                if i.split('-') :
                    i = i.split('—')
                    for i_part in i :
                        try:
                            if int(i_part):
                                if i_part :return i_part
                        except Exception as e : ...
                
        # if 'insta' in (response).lower():
        #     response = response.split(' ')
        #     otp = response[1]+response[2]
        #     return otp
        time.sleep(4)

def ban_number(phone_number, pid='8',country = 'sa'):
    url = "http://api.getsmscode.com/vndo.php?"
    payload = {
        "action": "addblack",
        "username": "pay@noborders.net",
        "token": "87269a810f4a59d407d0e0efe58185e6",
        "pid": pid,
        "mobile": phone_number,
        "author": "pay@noborders.net",
        "cocode":country
    }
    payload = urlencode(payload)
    full_url = url + payload
    response = requests.post(url=full_url)
    print(response.text)
    return response

# api_number = getsmscode('pay@noborders.net','87269a810f4a59d407d0e0efe58185e6')

# number = get_number()
# pluse_number = f'+{number}'
# print(number)
driver = get_driver("profile2",vpn=False)
change_number = True
for i in range(5):

    if change_number :
        number = get_number()
        pluse_number = f'+{number}'
        print(number)
        change_number = False
    driver.get('http://www.google.com')


    time.sleep(4)
    driver.find_element(By.CLASS_NAME,'gb_2').click()
    time.sleep(4)
    driver.find_element(By.XPATH,'//*[@id="yDmH0d"]/c-wiz/div/div[2]/div/div[2]/div/div[2]/div/div/div[1]/div/button').click()
    time.sleep(4)
    driver.find_element(By.XPATH,'//*[@id="yDmH0d"]/c-wiz/div/div[2]/div/div[2]/div/div[2]/div/div/div[2]/div/ul/li[1]').click()

    f_name = driver.find_element(By.XPATH,'//*[@id="firstName"]').send_keys('faduhgfkdaf')
    f_name = driver.find_element(By.XPATH,'//*[@id="lastName"]').send_keys('faduhgfkdsadadaf')
    f_name = driver.find_element(By.XPATH,'//*[@id="username"]').send_keys('faduhgfkdsadadaf')
    f_name = driver.find_element(By.XPATH,'//*[@id="passwd"]/div[1]/div/div[1]/input').send_keys('Riken@123')
    f_name = driver.find_element(By.XPATH,'//*[@id="confirm-passwd"]/div[1]/div/div[1]/input').send_keys('Riken@123')
    driver.find_element(By.XPATH,'//*[@id="accountDetailsNext"]/div/button').click()
    time.sleep(5)
    # add + before number


    time.sleep(4)
    driver.find_element(By.XPATH,'//*[@id="phoneNumberId"]').send_keys(pluse_number)
    driver.find_element(By.XPATH,'//*[@id="view_container"]/div/div/div[2]/div/div[2]/div/div[1]/div/div/button').click()
    try: 
        phone_notaccepted = driver.find_element(By.CLASS_NAME,'o6cuMc')
        if phone_notaccepted :
            change_number = True
            ban_number(number)
            continue
    except Exception as e:...
    
    # input('Enter 2:')
    
    time.sleep(10)
    number_otp = get_sms(number)
    print(number_otp,':  -----------1---------')
    if not number_otp : 
        change_number = True
        continue
    driver.find_element(By.XPATH,'//*[@id="code"]').send_keys(number_otp)
    time.sleep(4)
    driver.find_element(By.XPATH,'//*[@id="view_container"]/div/div/div[2]/div/div[2]/div/div[1]/div/div/button').click()
    time.sleep(5)




    from selenium.webdriver.support.ui import Select


    #month
    month_select = Select(driver.find_element(By.XPATH,'//*[@id="month"]'))
    month_select.select_by_value(str(random.randint(1,12)))
    # DAY
    driver.find_element(By.XPATH,'//*[@id="day"]').send_keys(random.randint(1,28))
    # year
    driver.find_element(By.XPATH,'//*[@id="year"]').send_keys(random.randint(1990,2003))

    # gender
    gender_select = Select(driver.find_element(By.XPATH,'//*[@id="gender"]'))
    gender_select.select_by_value(str(random.randint(1,3)))

    # next btn
    driver.find_element(By.XPATH,'//*[@id="view_container"]/div/div/div[2]/div/div[2]/div/div[1]/div/div/button').click()


    input('Enter :')
driver.quit()