import os
import ssl
import random
import httplib2
import logging
import googleapiclient.errors
import google_auth_oauthlib.flow
import googleapiclient.discovery
import google.oauth2.credentials
from oauth2client import GOOGLE_REVOKE_URI, GOOGLE_TOKEN_URI, client

from youtubebot.models import *
from googleapiclient.http import MediaFileUpload
from youtubebot.models import YoutubeAccount, YoutubeVideoUrl

# selenium
import time
import csv
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

scopes = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


def get_credentials():
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secrets.json"
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes
    )
    flow.run_local_server(port=8000, prompt="consent", authorization_prompt_message="")
    credentials = flow.credentials
    return credentials


def get_user_info(credentials):
    user_info_service = googleapiclient.discovery.build(
        "oauth2", "v2", credentials=credentials
    )
    user_info = user_info_service.userinfo().get().execute()
    return user_info


def time_sleep():
    wait_t = random.randint(0, 222)
    return wait_t


def video_like(credential, video_url):
    try:
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        api_service_name = "youtube"
        api_version = "v3"
        access = credential.__dict__["_refresh_token"]
        CLIENT_ID = credential.__dict__["_client_id"]
        CLIENT_SECRET = credential.__dict__["_client_secret"]
        GOOGLE_TOKEN_URI = credential.__dict__["_token_uri"]
        credentials = client.OAuth2Credentials(
            access_token=None,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            refresh_token=access,
            token_expiry=None,
            token_uri=GOOGLE_TOKEN_URI,
            user_agent=None,
        )
        credentials.refresh(httplib2.Http())
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials
        )
        video_id = video_url.split("=")[1]
        try:
            like = youtube.videos().rate(rating="like", id=video_id).execute()
            logging.info(
                "=====================  video like success=============================="
            )
            print("Like Job Done")
            return True
        except Exception as ex:
            logging.info(
                "===================== Youtube Video like errors =============================="
            )
            logging.info(str(ex))
            print(ex)
            return False

    except Exception as ex:
        logging.info(
            "===================== Youtube Video like errors =============================="
        )
        logging.info(str(ex))
        print(ex)
        return False


def video_dislike(credential, video_url):
    try:
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        api_service_name = "youtube"
        api_version = "v3"
        access = credential.__dict__["_refresh_token"]
        CLIENT_ID = credential.__dict__["_client_id"]
        CLIENT_SECRET = credential.__dict__["_client_secret"]
        GOOGLE_TOKEN_URI = credential.__dict__["_token_uri"]
        credentials = client.OAuth2Credentials(
            access_token=None,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            refresh_token=access,
            token_expiry=None,
            token_uri=GOOGLE_TOKEN_URI,
            user_agent=None,
        )
        credentials.refresh(httplib2.Http())
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials
        )
        video_id = video_url.split("=")[1]
        try:
            like = youtube.videos().rate(rating="dislike", id=video_id).execute()
            logging.info(
                "=====================  video dislike success=============================="
            )
            return True
        except Exception as ex:
            logging.info(
                "===================== Youtube Video dislike errors =============================="
            )
            logging.info(str(ex))
            print(ex)
            return False
    except Exception as ex:
        logging.info(
            "===================== Youtube Video dislike errors =============================="
        )
        logging.info(str(ex))
        print(ex)
        return False


def comment_on_video(credential, video_url, comments):
    try:
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        api_service_name = "youtube"
        api_version = "v3"
        access = credential.__dict__["_refresh_token"]
        CLIENT_ID = credential.__dict__["_client_id"]
        CLIENT_SECRET = credential.__dict__["_client_secret"]
        GOOGLE_TOKEN_URI = credential.__dict__["_token_uri"]
        credentials = client.OAuth2Credentials(
            access_token=None,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            refresh_token=access,
            token_expiry=None,
            token_uri=GOOGLE_TOKEN_URI,
            user_agent=None,
        )
        credentials.refresh(httplib2.Http())
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials
        )
        video_id = video_url.split("=")[1]
        try:
            comment = (
                youtube.commentThreads()
                .insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "videoId": video_id,
                            "topLevelComment": {"snippet": {"textOriginal": comments}},
                        }
                    },
                )
                .execute()
            )
            logging.info(
                "=====================  comment on video success=============================="
            )
            print("Done")
            return True
        except Exception as ex:
            logging.info(
                "===================== Youtube Video Comment errors =============================="
            )
            logging.info(str(ex))
            return False

    except Exception as ex:
        logging.info(
            "===================== Youtube Video Comment errors =============================="
        )
        logging.info(str(ex))
        return False


def subscribe_channel(credential, channel_id):
    try:
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        api_service_name = "youtube"
        api_version = "v3"
        # Get credentials and create an API client
        access = credential.__dict__["_refresh_token"]
        CLIENT_ID = credential.__dict__["_client_id"]
        CLIENT_SECRET = credential.__dict__["_client_secret"]
        GOOGLE_TOKEN_URI = credential.__dict__["_token_uri"]
        credentials = client.OAuth2Credentials(
            access_token=None,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            refresh_token=access,
            token_expiry=None,
            token_uri=GOOGLE_TOKEN_URI,
            user_agent=None,
        )
        credentials.refresh(httplib2.Http())
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials
        )
        try:
            request = (
                youtube.subscriptions()
                .insert(
                    part="snippet",
                    body={
                        "id": 1,
                        "snippet": {"resourceId": {"channelId": channel_id}},
                    },
                )
                .execute()
            )
            logging.info(
                "=====================  channel successfully subscribed =============================="
            )
            return True
        except Exception as ex:
            logging.info(
                "===================== channel subscribe errors =============================="
            )
            logging.info(str(ex))
            print(ex)
            return False
    except Exception as ex:
        logging.info(
            "===================== channel subscribe errors =============================="
        )
        logging.info(str(ex))
        print(ex)
        return False


def video_upload(credential, channel_id, video_id, title, description):
    try:
        scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"

        # Get credentials and create an API client
        access = credential.__dict__["_refresh_token"]
        CLIENT_ID = credential.__dict__["_client_id"]
        CLIENT_SECRET = credential.__dict__["_client_secret"]
        GOOGLE_TOKEN_URI = credential.__dict__["_token_uri"]
        credentials = client.OAuth2Credentials(
            access_token=None,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            refresh_token=access,
            token_expiry=None,
            token_uri=GOOGLE_TOKEN_URI,
            user_agent=None,
        )
        credentials.refresh(httplib2.Http())
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials
        )
        media = MediaFileUpload(video_id, mimetype="video/mp4")
        request = (
            youtube.videos()
            .insert(
                part="snippet",
                body={
                    "snippet": {
                        "catogryId": 20,
                        "title": title,
                        "description": description,
                    },
                },
                media_body=media,
            )
            .execute()
        )
        logging.info(
            "=====================  video upload successfully  =============================="
        )
        print(request)
        return True

    except Exception as ex:
        logging.info(
            "===================== video upload errors =============================="
        )
        logging.info(str(ex))
        print(ex)
        return False


def views_video(video_url, video_views):
    try:
        for i in range(int(video_views)):
            CONTENT_LIST = [{"content_type": "text", "data": "Lorem ipsum"}]
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            # chrome_options.add_argument("--headless")
            chrome_options.add_experimental_option(
                "excludeSwitches",
                [
                    "ignore-certificate-errors",
                    "safebrowsing-disable-download-protection",
                    "safebrowsing-disable-auto-update",
                    "disable-client-side-phishing-detection",
                ],
            )
            chrome_options.add_argument(
                "/usr/bin/google-chrome"
            )  # Path to your chrome profile
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(video_url)
            time.sleep(5)
            try:
                driver.find_element_by_xpath("//button[@aria-label='Play']").click()
                time.sleep(20)
            except:
                pass
            driver.close()
        logging.info(
            "=====================  video views successfully  =============================="
        )
        print("video views done")
        return True
    except Exception as ex:
        logging.info(
            "===================== video views errors =============================="
        )
        logging.info(str(ex))
        print(ex)
        return False