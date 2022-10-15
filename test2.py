
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



driver = get_driver('123334')
driver.get('http://www.google.com')
driver.get('https://accounts.google.com/signup/v2/webcreateaccount?biz=false&cc=IN&continue=https%3A%2F%2Fwww.google.com%3Fhl%3Den-GB&dsh=S-16160795%3A1665039827697251&flowEntry=SignUp&flowName=GlifWebSignIn&hl=en-GB')
input('ENter ;')
time.sleep(4)
driver.find_element(By.CLASS_NAME,'gb_2').click()
time.sleep(4)
driver.find_element(By.XPATH,'//*[@id="yDmH0d"]/c-wiz/div/div[2]/div/div[2]/div/div[2]/div/div/div[1]/div/button').click()
time.sleep(4)
driver.find_element(By.XPATH,'//*[@id="yDmH0d"]/c-wiz/div/div[2]/div/div[2]/div/div[2]/div/div/div[2]/div/ul/li[1]').click()
input('Enter 2')
driver.find_element(By.XPATH,'//*[@id="firstName"]').send_keys('fadudsdhgfkdaf')
driver.find_element(By.XPATH,'//*[@id="lastName"]').send_keys('faduhgfksadfdsadadaf')
driver.find_element(By.XPATH,'//*[@id="username"]').send_keys('faduhgfkddsdsadadaf')
driver.find_element(By.XPATH,'//*[@id="passwd"]/div[1]/div/div[1]/input').send_keys('Riken@123')
driver.find_element(By.XPATH,'//*[@id="confirm-passwd"]/div[1]/div/div[1]/input').send_keys('Riken@123')
driver.find_element(By.XPATH,'//*[@id="accountDetailsNext"]/div/button').click()
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