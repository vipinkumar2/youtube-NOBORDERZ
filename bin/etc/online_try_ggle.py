from selenium.webdriver import Chrome, ChromeOptions
import time
from selenium.webdriver.common.by import By

EMAIL_ID = "ahvjavjvcjjcvjgv5423@gmail.com"

def slow_typing(element, text):
   for character in text:
      element.send_keys(character)
      time.sleep(0.3)

# Visit chrome://version/ and copy profile path in place of '<chrome user profile>'
options = ChromeOptions().add_argument("--user-data-dir=profiles")
# from driver.driver import get_driver
from webdriver_manager.chrome import ChromeDriverManager

browser = Chrome(ChromeDriverManager().install(),chrome_options=options)
# browser = getdri
browser.get('http://gmail.com')

time.sleep(2)

# to accept cookie notification so that it doesn't interfere
try: 
   cookie_cta = browser.find_element(By.ID,'accept-cookie-notification')
   cookie_cta.click()
except Exception as e:...

# Navigate to Signup Page
try:
   button = browser.find_element(By.ID,'signupModalButton')
   button.click()
except Exception as e:...

time.sleep(2)

# Fill user's full name
username = browser.find_element(By.ID,'user_fudll_name')
# username.send_keys('John Doe')
slow_typing(username, 'John Doe')

time.sleep(1)
# Fill user's email ID
email = browser.find_element(By.ID,'user_email_login')
slow_typing(email, EMAIL_ID)

time.sleep(2)
# Fill user's password
password = browser.find_element(By.ID,'user_password')

# Reads password from a text file because
# it's silly to save the password in a script.
with open('password.txt', 'r') as myfile:
       Password = myfile.read().replace('\n', '')
slow_typing(password, Password)

time.sleep(1)
# click on Terms and Conditions
toc = browser.find_element_by_name('terms_and_conditions')
toc.click()

# click on signup page
signupbutton = browser.find_element(By.ID,'user_submit')
signupbutton.click()

time.sleep(20)

browser.close()