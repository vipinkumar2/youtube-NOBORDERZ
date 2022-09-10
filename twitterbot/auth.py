import random
from datetime import datetime
from time import sleep

import tweepy
from twitterbot.proxy import get_proxies, get_proxy
#
# CONSUMER_KEY = "8vEdUyeYYiuc94jzvVsPZoYzK"
# CONSUMER_SECRET = "7LwfwClVr570uxA2BRw9DYPnTErU7Ib8CZKczyon3PIxbgfjvo"


def rate_limit_status(api):
    rate_limit_data = api.rate_limit_status()

    """function to fetch with every API call, the rate limit status, and rest when we approach 92% of the allowable Twitter rate limit. """
    search_query = rate_limit_data["resources"]["tweets"]["/tweets/search/all"]
    search_query_recent = rate_limit_data["resources"]["tweets"][
        "/tweets/search/recent"
    ]
    usertimeline = rate_limit_data["resources"]["statuses"]["/statuses/lookup"]
    usertimeline_lookup = rate_limit_data["resources"]["statuses"][
        "/statuses/user_timeline"
    ]
    user = rate_limit_data["resources"]["users"]["/users/"]
    tweets = rate_limit_data["resources"]["tweets"]["/tweets/"]
    search_user = rate_limit_data["resources"]["users"]["/users/lookup"]
    user_favorites = rate_limit_data["resources"]["users"]["/users/:id/likes&POST"]
    media_upload = rate_limit_data["resources"]["media"]["/media/upload"]
    profile_update = rate_limit_data["resources"]["account"]["/account/update_profile"]

    """The permitted limit is 92% of the APIs allowable limit. After that, the app would be force to sleep till the reset time."""
    permitted_limit_search_query = 72
    permitted_limit_search_query_recent = 14
    permitted_limit_usertimeline = 72
    permitted_limit_usertimeline_lookup = 72
    permitted_limit_user = 72
    permitted_limit_tweets = 72
    permitted_limit_search_user = 72
    permitted_limit_user_favorites = 4
    permitted_limit_media_upload = 40
    permitted_limit_profile_update = 1

    if (
        search_query["remaining"] <= permitted_limit_search_query
        or search_query_recent["remaining"] <= permitted_limit_search_query_recent
        or usertimeline["remaining"] <= permitted_limit_usertimeline
        or usertimeline_lookup["remaining"] <= permitted_limit_usertimeline_lookup
        or user["remaining"] <= permitted_limit_user
        or tweets["remaining"] <= permitted_limit_tweets
        or search_user["remaining"] <= permitted_limit_search_user
        or user_favorites["remaining"] <= permitted_limit_user_favorites
        or media_upload["remaining"] <= permitted_limit_media_upload
        or profile_update["remaining"] <= permitted_limit_profile_update
    ):
        time_to_reset_unix_utc = datetime.utcfromtimestamp(profile_update["reset"])
        time_now = datetime.utcnow()
        time_now_unix = time_now.timestamp()
        time_difference = time_to_reset_unix_utc - time_now_unix

        sleep(time_difference)


# Authenticate to Twitter
def get_auth(consumer_key, consumer_secret, access_key, access_secret):
    while True:
        try:
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_key, access_secret,)
            api = tweepy.API(auth, proxy="gate.smartproxy.com:7000",
                             wait_on_rate_limit=True,)
            rate_limit_status(api)
            return api
        except ConnectionError:
            sleep(10)
            print("connection error.")
