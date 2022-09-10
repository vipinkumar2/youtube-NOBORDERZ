import traceback
import datetime
import tweepy
import time
import random
import traceback
from slack_logger import send_log
from twitterbot.utils import *
from twitterbot.constants import *
from twitterbot.models import *
from django.db.models import Q
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Scrape Tweet data and save in database if like greater then 1000"

    def get_account_qs(self):
        account_qs = TwitterAccount.objects.filter(status="ACTIVE")
        return account_qs

    def get_api(self,consumer_key, consumer_secret, access_key, access_secret):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(
            auth, proxy="gate.smartproxy.com:7000", wait_on_rate_limit=True
        )
        return api

    def get_target_account(self, action_qs, by_twitter_account):
        by_screen_name = by_twitter_account.screen_name
        followed_accounts = list(
            action_qs.filter(action_type="FOLLOW").values_list(
                "target_screen_name", flat=True
            )
        ) + list(by_screen_name)
        target_account = list(
            TwitterAccount.objects.filter(status="ACTIVE")
            .exclude(screen_name__in=followed_accounts)
            .values_list("screen_name", flat=True)
        )
        return target_account + [
            "Breaking_NFT",
            "Breaking_deFi",
            "Breaking_BSC",
            "Breaking_Dapps",
        ]

    def handle(self, *args, **options):
        while True:
            time.sleep(random.randrange(60, 120))
            today = datetime.datetime.now().date()
            account_qs = self.get_account_qs()
            for account in account_qs:
                time.sleep(random.randrange(60, 120))
                try:
                    print(f"{account.screen_name} --- started action --------\n")
                    """
                    Tweepy API initialization
                    """
                    api = self.get_api(account.consumer_key, account.consumer_secret, account.access_key, account.access_secret)

                    action_qs = TwitterActionLog.objects.filter(
                        twitter_account_id=account.id
                    ).exclude(action_type="TRACEBACK")
                    total_actions_today = action_qs.filter(created__date=today).count()

                    """
                    Follow Engagement Action
                    """
                    target_account = self.get_target_account(action_qs, account)
                    if (
                        total_actions_today < 5
                        and len(target_account)
                        and random.choice([0, 0, 1, 0, 0])
                    ):
                        time.sleep(random.randrange(300, 600))
                        random.shuffle(target_account)
                        screen_name = target_account[0]
                        # follow action using tweepy api
                        resp = api.create_friendship(
                            screen_name=screen_name, follow=True
                        )
                        """
                        Follow action log
                        """
                        TwitterActionLog.objects.create(
                            twitter_account=account,
                            action_type="FOLLOW",
                            target_id=screen_name,
                            target_screen_name=screen_name,
                            api_response=resp._json,
                        )
                        print(f"follow action completed")

                    """
                    Tweet on account
                    """
                    tweeted = TwitterActionLog.objects.filter(
                        action_type="TWEET", created__date=today
                    )
                    if not tweeted.exists() and random.choice([0, 0, 1, 0, 0]):
                        time.sleep(random.randrange(300, 600))
                        update_instance = UpdateTwitterAccount(account.id)
                        # tweet one art image
                        resp = update_instance.tweet_art_image()
                        """
                        Tweet action log
                        """
                        TwitterActionLog.objects.create(
                            twitter_account=account,
                            action_type="FOLLOW",
                            target_id=account.screen_name,
                            target_screen_name=account.screen_name,
                            api_response=resp._json if resp else False,
                        )
                        print(f"tweet action completed")

                    """
                    Like tweet action
                    """
                    target_account = self.get_target_account(action_qs, account)
                    if (
                        total_actions_today < 5
                        and len(target_account)
                        and random.choice([0, 0, 1, 0, 0])
                    ):
                        time.sleep(random.randrange(300, 600))
                        random.shuffle(target_account)
                        screen_name = target_account[0]
                        tweets = api.user_timeline(screen_name=screen_name)
                        random.shuffle(tweets)
                        for tweet in tweets:
                            if not tweet.favorited:
                                resp = api.create_favorite(tweet.id)
                                """
                                Tweet action log
                                """
                                TwitterActionLog.objects.create(
                                    twitter_account=account,
                                    action_type="LIKE",
                                    target_id=tweet.id,
                                    target_screen_name=screen_name,
                                    api_response=resp._json if resp else False,
                                )
                                print(f"tweet action completed")
                                break

                        """
                        Retweet action
                        """
                        target_account = self.get_target_account(action_qs, account)
                        if (
                            total_actions_today < 5
                            and len(target_account)
                            and random.choice([0, 0, 1, 0, 0])
                        ):
                            time.sleep(random.randrange(300, 600))
                            random.shuffle(target_account)
                            screen_name = target_account[0]
                            tweets = api.user_timeline(screen_name=screen_name)
                            random.shuffle(tweets)
                            for tweet in tweets:
                                if not tweet.favorited:
                                    if not tweet.retweeted:
                                        resp = api.retweet(tweet.id)
                                        """
                                        Retweet action log
                                        """
                                        TwitterActionLog.objects.create(
                                            twitter_account=account,
                                            action_type="RETWEET",
                                            target_id=tweet.id,
                                            target_screen_name=screen_name,
                                            api_response=resp._json if resp else False,
                                        )
                                        print(f"tweet action completed")
                                        break

                    print(f"{account.screen_name} --- end action ---------")
                except tweepy.TweepError as tweepy_error:
                    error = tweepy_error.reason
                    error_log = f"Account: {account.screen_name},\n {error}"

                    error_msg = error[0]["message"]

                    if "This request looks like it might be automated" in error_msg:
                        account.status = "INACTIVE"
                        account.save()

                    elif (
                        "Your account is suspended and is not permitted to access this feature."
                        in error_msg
                    ):
                        account.status = "INACTIVE"
                        account.save()

                    else:
                        account.status = "BANNED"
                        account.save()

                    print(error_log)

                    TwitterActionLog.objects.create(
                        twitter_account=account,
                        action_type="TRACEBACK",
                        target_id=account.screen_name,
                        target_screen_name=account.screen_name,
                        api_response=error,
                    )
                    send_log(log_type="Twitter Engagement Error: ", error=error_log)
                except Exception as e:
                    error = traceback.format_exc()
                    TwitterActionLog.objects.create(
                        twitter_account=account,
                        action_type="TRACEBACK",
                        target_id=account.screen_name,
                        target_screen_name=account.screen_name,
                        api_response=error,
                    )
                    send_log("ENGAGEMENT_EACH_OTHER_ACTION", error)
