import tweepy
from PIL import Image
import unicodecsv
import re
import os
import math
import time
import random
from twitterbot.models import *
from django.conf import settings
from twitterbot.proxy import get_proxies, get_proxy
import boto3
import requests
import os
from urllib.parse import urlparse
from twitterbot import constants as constant
import traceback
import urllib.parse as urlparse
from urllib.parse import parse_qs
from langdetect import detect


class UpdateTwitterAccount:
    def __init__(self, acc_id):
        twitter_acc_qs = TwitterAccount.objects.filter(id=acc_id)

        if twitter_acc_qs.exists():
            
            self.twitter_account = twitter_acc_qs.last()
            self.consumer_key = self.twitter_account.consumer_key
            self.consumer_secret = self.twitter_account.consumer_secret
            self.access_key = self.twitter_account.access_key
            self.access_secret = self.twitter_account.access_secret
            self.country = self.twitter_account.country

            """
            tweepy API initialization
            """
            self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
            self.auth.set_access_token(
                self.access_key,
                self.access_secret,
            )
            self.api = tweepy.API(
                self.auth,
                proxy=self.get_proxy(self.country),
                wait_on_rate_limit=True,
                wait_on_rate_limit_notify=True,
            )
            self.me = self.api.me()
            """
            fetch images from directory
            """
            self.directory = f"{settings.ART_IMAGE_DIR}/pixabay_{random.randint(1, 6)}/"
            os.chdir(self.directory)
            self.images = os.listdir()

    def compress_images(directory=False, quality=30):
        """
        Compress images size
        """
        if directory:
            os.chdir(directory)
        files = os.listdir()
        images = [file for file in files if file.endswith(("jpg", "png"))]
        for image in images:
            img = Image.open(image)
            img.save(
                "Compressed_and_resized_with_function_" + image,
                optimize=True,
                quality=quality,
            )

    def get_random_wait(self, initial_limit=1, upper_limit=5):
        return random.randint(initial_limit, upper_limit)

    def update_profile_pic(self):
        """
        Update twitter account profile picture with ART type image
        """
        random.shuffle(self.images)
        random.shuffle(self.images)
        random.shuffle(self.images)
        response = False
        for image in self.images:
            try:
                img_full_path = self.directory + image
                img_size = os.stat(img_full_path).st_size
                if int(img_size) >= 600:
                    self.resize_image(img_full_path)
                time.sleep(self.get_random_wait(initial_limit=10, upper_limit=20))
                response = self.api.update_profile_image(img_full_path)
                print("profile picture udpated successfully.")
                break

            except Exception as e:
                print(f"Profile picture update error: {e}.")
                pass
        return response

    def update_banner(self):
        """
        Update twitter account banner image with ART type image
        """
        random.shuffle(self.images)
        random.shuffle(self.images)
        random.shuffle(self.images)
        response = False
        for image in self.images:
            try:
                img_full_path = self.directory + image
                img_size = os.stat(img_full_path).st_size
                if int(img_size) >= 600:
                    self.resize_image(img_full_path)
                time.sleep(self.get_random_wait(initial_limit=10, upper_limit=20))
                response = self.api.update_profile_banner(self.directory + image)
                print("banner image uploaded successfully.")
                break

            except Exception as e:
                print(f"Profile banner update error: {e}.")
                pass
        return response

    def update_bio_description(self, description):
        response = self.api.update_profile(description=description)
        return response

    def resize_image(self, img_full_path):
        basewidth = 700
        img = Image.open(img_full_path)
        wpercent = basewidth / float(img.size[0])
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), Image.ANTIALIAS)
        img.save(img_full_path)
        return img_full_path

    def tweet_art_image(self):
        """
        Tweet image with ART type.
        """
        random.shuffle(self.images)
        random.shuffle(self.images)
        random.shuffle(self.images)
        response = False
        for image in self.images:
            try:
                img_full_path = self.directory + image
                img_size = os.stat(img_full_path).st_size
                if int(img_size) >= 600:
                    self.resize_image(img_full_path)
                time.sleep(self.get_random_wait(initial_limit=10, upper_limit=20))
                response = self.api.update_with_media(img_full_path)
                print("image tweeted successfully")
                break

            except Exception as e:
                print(f"tweet image error: {e}.")
                pass
        return response

    def update_profile(self):
        art_profiles = TwitterAccount.objects.filter(account_type="ART")
        profile_update_response = []

        """
        update profile picture 
        """
        update_pic_res = self.update_profile_pic()
        profile_update_response.append(
            update_pic_res._json if update_pic_res else update_pic_res
        )
        time.sleep(self.get_random_wait(initial_limit=45, upper_limit=90))

        """
        update banner image
        """
        if random.choice([0, 0, 0, 1]):
            update_banner_res = self.update_banner()
            profile_update_response.append(
                update_banner_res._json if update_banner_res else update_banner_res
            )
            time.sleep(self.get_random_wait(initial_limit=45, upper_limit=90))

        """
        tweet one image
        """
        if random.choice([0, 0, 0, 1]):
            tweet_res = self.tweet_art_image()
            profile_update_response.append(tweet_res._json if tweet_res else tweet_res)
            time.sleep(self.get_random_wait(initial_limit=45, upper_limit=90))

        """
        update profile bio
        """
        bio_resp = self.update_bio_description(random.choice(constant.TWITTER_BIOS))
        profile_update_response.append(bio_resp._json if bio_resp else bio_resp)
        time.sleep(self.get_random_wait(initial_limit=45, upper_limit=90))

        """
        Follow
        """
        if random.choice([0, 0, 0, 1]):
            target_account = random.choice(art_profiles)
            screen_name = target_account.screen_name

            follow_resp = self.api.create_friendship(
                screen_name=screen_name, follow=True
            )

            TwitterActionLog.objects.create(
                twitter_account=self.twitter_account,
                action_type="FOLLOW",
                target_id=screen_name,
                target_screen_name=screen_name,
                api_response=follow_resp._json if follow_resp else False,
            )

            profile_update_response.append(
                follow_resp._json if follow_resp else follow_resp
            )
            time.sleep(self.get_random_wait(initial_limit=45, upper_limit=90))

        """
        Like Tweet
        """
        if random.choice([0, 0, 0, 1]):
            target_account = random.choice(art_profiles)
            screen_name = target_account.screen_name

            tweets = self.api.user_timeline(screen_name=screen_name)
            random.shuffle(tweets)
            for tweet in tweets:
                if not tweet.favorited:
                    like_resp = self.api.create_favorite(tweet.id)
                    """
                    Tweet action log
                    """
                    TwitterActionLog.objects.create(
                        twitter_account=self.twitter_account,
                        action_type="LIKE",
                        target_id=tweet.id,
                        target_screen_name=screen_name,
                        api_response=like_resp._json if like_resp else False,
                    )
                    break

            profile_update_response.append(like_resp._json if like_resp else like_resp)
            time.sleep(self.get_random_wait(initial_limit=45, upper_limit=90))

        return profile_update_response

    def get_proxy(self, country):
        code = (
            requests.get(f"https://restcountries.eu/rest/v2/name/{country}").json()[0][
                "alpha2Code"
            ]
        ).lower()
        proxy = f"{code}.smartproxy.com:10000"
        return proxy


def move_link_to_s3(url="", file_type="image", tweet_id=None):
    """
    :param url:
    :param file_type:
    :param tweet_id:
    :return: upload the media link on twitter
    """
    file_url = ""
    s3 = boto3.resource(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name="ap-southeast-1",
    )

    response = requests.get(url)
    if response.status_code == 200:
        raw_data = response.content
        url_parser = urlparse.urlparse(url)
        file_name = os.path.basename(url_parser.path)
        key = file_type + f"/surviral_web/{tweet_id}/" + file_name

        try:
            with open(file_name, "wb") as new_file:
                new_file.write(raw_data)

            data = open(file_name, "rb")
            s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).put_object(Key=key, Body=data)
            data.close()

            file_url = "https://%s.%s/%s" % (
                settings.AWS_STORAGE_BUCKET_NAME,
                "s3.ap-southeast-1.amazonaws.com",
                key,
            )
        except Exception as e:
            print("Error in file upload %s." % (str(e)))

        finally:
            # Close and remove file from Server
            new_file.close()
            os.remove(file_name)
            print("Attachment Successfully save in S3 Bucket url %s " % (file_url))
    else:
        print("Cannot parse url")
    return file_url


class ScrapeTweet:
    """
    scrape tweet data from screen name and save in database if like greater then 1000
    """

    def __init__(self):
        self.auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
        self.auth.set_access_token(settings.ACCESS_KEY, settings.ACCESS_SECRET)
        # self.api = tweepy.API(self.auth, proxy="gate.smartproxy.com:7000")
        self.api = tweepy.API(self.auth)

    def save_tweet_data(self, hashtags):
        for tag in hashtags.split(","):
            new_tweets = []
            tweets = self.api.search(
                q=tag, result_type="popular", tweet_mode="extended", count=200, rpp=1
            )

            while tweets.next_results:
                print(len(tweets))
                new_tweets += [tweet for tweet in tweets]
                parsed = urlparse.urlparse(tweets.next_results)
                parsed_params = parse_qs(parsed.query)
                print(parsed_params)
                tweets = self.api.search(
                    q=tag,
                    result_type="popular",
                    max_id=parsed_params["max_id"][0],
                    tweet_mode="extended",
                    count=200,
                    rpp=1,
                )
            for tweet in new_tweets:
                if not Tweet.objects.filter(tweet_id=tweet.id).exists():
                    tweet_url = f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
                    try:
                        print(f"saving info of tweet id ------------- {tweet.id}")
                        tweet_obj = Tweet.objects.create(
                            tweet_id=tweet.id,
                            text=tweet.full_text,
                            tweet_meta=tweet._json,
                            likes=tweet.favorite_count,
                            retweet=tweet.retweet_count,
                            screen_name=tag,
                        )
                        media_image = list()
                        media_video = list()
                        tweet_data = {
                            "tweet_url": tweet_url,
                            "api_response": tweet._json,
                        }
                        tweet_obj.tweet_meta = tweet_data
                        tweet_obj.save()
                        try:
                            tweet_json = tweet._json
                            if "extended_entities" in tweet_json:
                                video_list = tweet.extended_entities["media"]
                                for item in video_list:
                                    if item["type"] == "video":
                                        media_video.append(
                                            item["video_info"]["variants"][-1]["url"]
                                        )
                        except Exception as ex:
                            print(f"No Video exist for tweet id {tweet.id}")

                        if "media" in tweet.entities:
                            media_list = tweet.entities["media"]
                            for item in media_list:
                                if item["type"] == "photo":
                                    media_image.append(item["media_url_https"])

                            tweet_obj.image = media_image
                            tweet_obj.video = media_video
                            tweet_obj.save()
                        else:
                            continue

                    except:
                        error = traceback.format_exc()
                        print(error)
                        pass


def remove_unwanted_characters(string):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U00010000-\U0010ffff"
        "]+",
        flags=re.UNICODE,
    )
    demoji = emoji_pattern.sub(r"", string)
    links_removed = re.sub(
        r"\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*", "", demoji
    )
    string_list = links_removed.replace("#", "").replace("@", "").split(".")
    final_string = ""
    for string_part in string_list:
        try:
            if detect(string_part) == "en":
                final_string += string_part
        except:
            pass

    return final_string


def write_output(data):
    path = "/home/angelium/dev/scraped_data.csv"
    with open(path, mode="ab") as csvFile:
        row = unicodecsv.writer(csvFile, delimiter=",", lineterminator="\n")
        row.writerow(data)


class MediaAccountPosting:
    def __init__(self):
        self.media_accounts = TwitterAccount.objects.filter(
            account_type="MKT_MEDIA"
        ).filter(status="ACTIVE")

    def get_api(self, acc_id):
        # Media twitter app credentials
        app_consumer_key = "4U97ik8wddJOTmObOw5ejAUSt"
        app_consumer_secret = "gL9DzwDXrqKLWDiGT0KW6J1s1VkzyxjO3uWTdzY4LnPdYl9KYa"
        app_access_token = "1361304377525370881-bucZ9yhfVv7pufq1Cg1JGdq2tDiMC1"
        app_access_secret = "sAx15Mu6RLvum1P4syt8fj8JLjx4ytQwvJ4RtiR9Uy49G"

        usr_acc = TwitterAccount.objects.get(id=acc_id)
        auth = tweepy.OAuthHandler(app_consumer_key, app_consumer_secret)
        auth.set_access_token(
            usr_acc.access_key,
            usr_acc.access_secret,
        )
        api = tweepy.API(auth)

        return api

    def make_post(self, api, tweet_text, tweet_media_path):
        resp = api.update_with_media(status=tweet_text, filename=tweet_media_path)
        return resp._json

    def do(self):
        # for i in range(5):

        for acc in self.media_accounts:
            acc = TwitterAccount.objects.get(id=acc.id)
            print(acc, acc.status)
            if acc.status == "ACTIVE":

                # get text/media from AI
                tweet_text = "HAPPY NATIONAL EMPANADA DAY!"
                tweet_media_path = "/home/angelium/Downloads/media_testing.jpg"

                api = self.get_api(acc_id=acc.id)

                try:
                    action_resp = self.make_post(api, tweet_text, tweet_media_path)

                    TwitterActionLog.objects.create(
                        twitter_account=acc,
                        action_type="MEDIA_POST",
                        api_response=action_resp,
                    )

                    print(
                        f"Successfully Posted on {acc.screen_name}| Text: {tweet_text} ||| Media_Path: {tweet_media_path} |"
                    )

                except tweepy.error.TweepError:
                    error = traceback.format_exc()
                    error_log = f"Account: {acc.screen_name}, error: {error}"
                    print(error_log)
                    if "To protect our users from spam" in error:
                        TwitterAccount.objects.filter(id=acc.id).update(status="BANNED")
                    TwitterActionLog.objects.create(
                        twitter_account=acc,
                        action_type="TRACEBACK",
                        api_response=error,
                    )

                rand_time = random.randrange(2600, 3000)
                print(f"Sleeping For {rand_time/60} minutes!")
                time.sleep(rand_time)
