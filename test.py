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


recovery_email = 'rikenkhadela85@gmail.com'
profile_name = str(random.randint(100000,9999999))
print(f'profile_name : {profile_name}')
password = 'Noborderz@123'
def random_sleep(a = 10, b = 16):
    time.sleep(random.randint(a,b))
    
def new_tab(driver,link='www.google.com',refresh_needed = False):
    """open a new tab and open link which is given else it will open google search bar"""
    driver.execute_script(f"window.open('{link}')")
    driver.switch_to.window(driver.window_handles[-1]) 
    if refresh_needed :driver.refresh()
    
    
link_list = [
    'https://www.google.com',
    'https://www.youtube.com',
    'https://www.twitter.com',
    'https://www.facebook.com',
    'https://www.apple.com/in/',
    'https://www.https://github.com/',
    'https://web.telegram.org/k/#@xanaofficial',
    'https://stackoverflow.com/',
    'https://computingforgeeks.com/installing-postgresql-database-server-on-ubuntu/'
]
def get_number(pid='1',country = 'my'):
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
        if str(response) == 'Message|Capture Max mobile numbers,you max is 5':
            continue
        else:break
    return response

def get_sms(phone_number, pid='1',country = 'my'):
    print('phone_number : ',phone_number)
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
    for x in range(20):
        response = requests.post(url=full_url).text
        if "Google verification" in response:
            response = response.split(' ')
            for i in response : 
                if i.split('-') :
                    i = i.split('—')
                    for i_part in i :
                        try:
                            if int(i_part):
                                return i_part
                        except Exception as e : ...
        time.sleep(10)

    return False

def ban_number(phone_number, pid='1',country = 'my'):
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
    print('response : ',response.text)
    return response

def fake_name():
    from faker import Faker
    fake = Faker()
    name = fake.name()
    name_li = str(name).split(' ')
    fname = name_li[0]
    lname = name_li[-1]
    return name,fname, lname

driver = get_driver(profile_name,vpn=False)
change_number = True
for i in range(5):

    for _ in range(5):
        
        if change_number :
            number = get_number()
            pluse_number = f'+{number}'
            print('number :',number)
            change_number = False
        driver.get('http://www.google.com')

        # input('dfvd')
        name,fname, lname = fake_name()
        random_sleep()
        driver.find_element(By.CLASS_NAME,'gb_2').click()
        random_sleep()
        driver.find_element(By.XPATH,'//*[@id="yDmH0d"]/c-wiz/div/div[2]/div/div[2]/div/div[2]/div/div/div[1]/div/button').click()
        random_sleep()
        driver.find_element(By.XPATH,'//*[@id="yDmH0d"]/c-wiz/div/div[2]/div/div[2]/div/div[2]/div/div/div[2]/div/ul/li[1]').click()

        f_name = driver.find_element(By.XPATH,'//*[@id="firstName"]').send_keys(fname)
        f_name = driver.find_element(By.XPATH,'//*[@id="lastName"]').send_keys(lname)
        name = name.split(' ')
        name = name[0]+name[1]
        email = str(name)+str(random.randint(10000,999999))
        print('email :',email)
        f_name = driver.find_element(By.XPATH,'//*[@id="username"]').send_keys(email)
        f_name = driver.find_element(By.XPATH,'//*[@id="passwd"]/div[1]/div/div[1]/input').send_keys(password)
        f_name = driver.find_element(By.XPATH,'//*[@id="confirm-passwd"]/div[1]/div/div[1]/input').send_keys(password)
        driver.find_element(By.XPATH,'//*[@id="accountDetailsNext"]/div/button').click()
        random_sleep()
        # add + before number

        random_sleep()
        driver.find_element(By.XPATH,'//*[@id="phoneNumberId"]').send_keys(pluse_number)
        driver.find_element(By.XPATH,'//*[@id="view_container"]/div/div/div[2]/div/div[2]/div/div[1]/div/div/button').click()
        random_sleep(7,12)
        try: 
            phone_notaccepted = driver.find_element(By.CLASS_NAME,'o6cuMc')
            if phone_notaccepted : 
                change_number = True
                ban_number(number)
            continue
        except Exception as e:...
    
    
        number_otp = get_sms(number)
        print('number_otp :',number_otp)
        if not number_otp : 
            change_number = True
            ban_number(number)
            continue
        driver.find_element(By.XPATH,'//*[@id="code"]').send_keys(number_otp)
        random_sleep()
        # input('Enter 1 :')
        driver.find_element(By.XPATH,'//*[@id="view_container"]/div/div/div[2]/div/div[2]/div/div[1]/div/div/button').click()
        random_sleep()

        # input('Enter 2 :')


        from selenium.webdriver.support.ui import Select

        driver.find_element(By.XPATH,'//*[@id="view_container"]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[2]/div[1]/div/div[1]/div/div[1]/input').send_keys(recovery_email)
        
        
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

        random_sleep()
        # yes i'm
        driver.find_element(By.XPATH,'//*[@id="view_container"]/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div/button').click()
        
        # i agree  (scroll karavanu baki)
        random_sleep()
        driver.find_element(By.XPATH,'//*[@id="view_container"]/div/div/div[2]/div/div[2]/div/div[1]/div/div/button').click()
        random_sleep()
        # for link in link_list:
        #     new_tab(driver=driver,link=link,refresh_needed=True)
        # random_sleep(10,12)
        for i in range(4):driver.get('https://www.youtube.com')
        
        input('Enter :')
        driver.quit()
        
        
        