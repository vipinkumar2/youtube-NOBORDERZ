import time

import clipboard
import tweepy
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


def browser_profile():
    browserProfile = webdriver.ChromeOptions()
    # prefs = {
    #     "translate_whitelists": {"pl": "en"},
    #     "translate": {"enabled": "true"}
    # }
    browserProfile.add_argument("--disable-extensions")
    browserProfile.add_argument("--enable-javascript")
    browserProfile.add_argument("--disable-popup-blocking")
    browserProfile.add_argument("--start-maximized")
    browserProfile.add_argument("--disable-blink-features=AutomationControlled")
    browserProfile.add_experimental_option("excludeSwitches", ["enable-automation"])
    browserProfile.add_experimental_option("useAutomationExtension", False)
    # browserProfile.add_experimental_option("prefs", prefs)
    return browserProfile


def login_twitter(driver, username, password, phone_number):
    consumer_key, consumer_secret = settings.CONSUMER_KEY, settings.CONSUMER_SECRET
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    url = auth.get_authorization_url()
    # open_page(driver)
    driver.get(url)
    time.sleep(3)
    username_ele = driver.find_element_by_id("username_or_email")
    if username_ele:
        time.sleep(2)
        username_ele.click()
        time.sleep(2)
        # clipboard.copy(username)
        username_ele.send_keys(username)
    time.sleep(3)

    password_ele = driver.find_element_by_id("password")
    if password_ele:
        time.sleep(2)
        password_ele.click()
        time.sleep(2)
        # clipboard.copy(password)
        password_ele.send_keys(password)
    time.sleep(2)

    authorise_btn = driver.find_elements_by_xpath(
        '//input[@class="submit button selected"]'
    )
    if authorise_btn:
        time.sleep(3)
        authorise_btn[0].click()

    time.sleep(5)

    try:
        verifier = str(driver.current_url).split("=")[-1]
        key, secret = auth.get_access_token(verifier)
        print(key, secret)
        driver.close()
    except Exception:

        err_msg = driver.find_elements_by_xpath(
            '//div[text()="The username and password that you entered did not '
            'match our records. Please double-check and try again."]'
        )
        if err_msg:
            print("credentials mismatch")
            driver.close()

        sub = driver.find_elements_by_id("allow")
        if sub:
            sub[0].click()
            time.sleep(3)
            verifier = str(driver.current_url).split("=")[-1]
            key, secret = auth.get_access_token(verifier)
            print(key, secret)
            driver.close()

        phone_req_ele = driver.find_elements_by_id("challenge_response")
        if phone_req_ele:
            phone_req_ele[0].send_keys(phone_number)
            time.sleep(2)

            sub = driver.find_element_by_id("email_challenge_submit")
            if sub:
                sub.click()
            time.sleep(2)
            if input("press enter"):
                pass
            return login_twitter(driver, username, password, phone_number)
        else:
            if input("press enter"):
                pass
            return login_twitter(driver, username, password, phone_number)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("username", type=str)
        parser.add_argument("password", type=str)
        parser.add_argument("phone", type=str)

    def handle(self, *args, **options):
        driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=browser_profile()
        )
        login_twitter(
            driver, options["username"], options["password"], options["phone"]
        )
