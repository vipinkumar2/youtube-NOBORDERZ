import logging
from twitterbot.models import TwitterAccount

from twitterbot.auth import *
from django.conf import settings


class TwitterAccountEngagement:
    def __init__(self, acc_id, target_username, tweet_id=False):
        twitter_acc = TwitterAccount.objects.filter(id=acc_id)

        if twitter_acc:
            self.twitter_account = twitter_acc.last()
            self.target_username = target_username
            self.access_key = self.twitter_account.access_key
            self.access_secret = self.twitter_account.access_secret
            self.consumer_key = self.twitter_account.consumer_key
            self.consumer_secret = self.twitter_account.consumer_secret
            self.api = get_auth(
                self.consumer_key,
                self.consumer_secret,
                self.access_key,
                self.access_secret,
            )
            self.user_data = self.api.get_user(self.target_username)._json
            self.user_id = self.user_data["id"]
            self.name = self.user_data["name"]
            self.screen_name = self.user_data["screen_name"]
            self.recent_tweet = (
                self.get_tweet(tweet_id) if tweet_id else self.get_most_recent_tweet()
            )
            self.recent_tweet_id = self.recent_tweet.id

    def get_tweet(self, tweet_id):
        tweet = self.api.get_status(tweet_id)
        return tweet

    def get_most_recent_tweet(self):
        # Get most recent 20 tweets of the target user
        recent_tweets = self.api.user_timeline(
            user_id=self.user_id, tweet_mode="extended"
        )

        # Most recent tweet of target user
        most_recent_tweet = recent_tweets[0]

        return most_recent_tweet

    def follow(self, screen_name=False):
        if not self.recent_tweet.user.following:
            resp = self.api.create_friendship(self.user_id)
            resp = resp._json
        else:
            resp = {"error": "already following"}
        return resp

    def like(self, tweet_id):
        if not self.recent_tweet.favorited:
            resp = self.api.create_favorite(tweet_id)
            resp = resp._json
        else:
            resp = {"error": "already favorited"}
        return resp

    def retweet(self, tweet_id):
        resp = self.api.retweet(tweet_id)
        return resp

    def retweet_recent(self, tweet_id=False):
        if not self.recent_tweet.retweeted:
            resp = self.api.retweet(self.recent_tweet_id)
            resp = resp._json
        else:
            resp = {"error": "already retweeted"}
        return resp

    def comment(self, comment, tweet_id=False):
        final_comment = f"@{self.recent_tweet.user.screen_name} {comment}"
        resp = self.api.update_status(
            final_comment,
            in_reply_to_status_id=self.recent_tweet_id,
        )
        resp = resp._json
        return resp
