import random
import time
import traceback
import datetime
import tweepy
from django.core.management.base import BaseCommand
from django.conf import settings
from slack_logger import send_log
from twitterbot.account_engagement import TwitterAccountEngagement
from twitterbot.models import *
from twitterbot.auth import get_auth
from twitterbot.constants import TWITTER_COMMENTS


class Command(BaseCommand):
    help = "Twitter Account Engagement"

    def add_arguments(self, parser):
        parser.add_argument(
            "--target_username",
            default=False,
            help="target username for twitter engagement.",
        )

        parser.add_argument(
            "--is_test",
            default=False,
            help="testing accounts only",
        )

        parser.add_argument(
            "--count",
            default=False,
            help="No. of user need to updated",
        )

        parser.add_argument(
            "--only_like",
            default=False,
            help="Only like account recent tweet",
        )

        parser.add_argument(
            "--latest_tweet_automation",
            default=False,
            help="Only like account recent tweet",
        )

        parser.add_argument(
            "--tweet_url",
            default=False,
            help="Only like account with tweet url",
        )

        parser.add_argument(
            "--account_type",
            default=False,
            help="Account type of twitter accounts",
        )

        parser.add_argument(
            "--created_today",
            default=False,
            help="Account type of twitter accounts",
        )

    def handle(self, *args, **kwargs):
        target_username = kwargs.get("target_username")
        is_test = kwargs.get("is_test")
        count = kwargs.get("count") if kwargs.get("count") else 50
        only_like = kwargs.get("only_like")
        latest_tweet_automation = kwargs.get("latest_tweet_automation")
        tweet_url = kwargs.get("tweet_url")
        account_type = kwargs.get("account_type")
        created_today = kwargs.get("created_today")

        while True:
            executable_tweet = []
            # print(f"\n=============waiting around 15 min.==========================")
            # time.sleep(random.randrange(900, 1000))
            # print(f"=================wait end, action started====================\n")

            if latest_tweet_automation:
                api = get_auth(
                    settings.CONSUMER_KEY,
                    settings.CONSUMER_SECRET,
                    settings.ACCESS_KEY,
                    settings.ACCESS_SECRET,
                )
                tweets = api.user_timeline(screen_name=target_username)
                new_tweets = [
                    x.id
                    for x in tweets
                    if x.created_at.date() == datetime.datetime.now().date()
                ]
                for n_t in new_tweets:
                    logs = TwitterActionLog.objects.filter(target_id=n_t).exclude(
                        action_type="TRACEBACK"
                    )
                    if logs.count() < 50:
                        executable_tweet.append(n_t)

                random.shuffle(executable_tweet)
                random.shuffle(executable_tweet)
            else:
                executable_tweet = []

            if tweet_url:
                tweet_id = tweet_url.split("status/")[1].split("?")[0]
                executable_tweet.append(tweet_id)

            if is_test:
                twitter_accounts_qs = TwitterAccount.objects.filter(
                    access_key__isnull=False,
                    access_secret__isnull=False,
                    status="TESTING",
                )
            else:
                excluded_acc = list(
                    TwitterActionLog.objects.filter(target_id__in=executable_tweet)
                    .distinct("twitter_account_id")
                    .values_list("twitter_account_id", flat=True)
                )
                updated_accounts = list(
                    TwitterJob.objects.filter(
                        job_type="UPDATE_ART_PROFILE", status="C"
                    ).values_list("twitter_account__id", flat=True)
                )
                twitter_accounts_qs = TwitterAccount.objects.filter(
                    id__in=updated_accounts,
                    access_key__isnull=False,
                    access_secret__isnull=False,
                    status="ACTIVE",
                    account_type=account_type if account_type else "XANALIANFT",
                ).exclude(id__in=excluded_acc)
            if created_today:
                today = datetime.datetime.now().date()
                twitter_accounts_qs = twitter_accounts_qs.filter(created__date=today)
            twitter_accounts_qs = list(twitter_accounts_qs)
            random.shuffle(twitter_accounts_qs)
            random.shuffle(twitter_accounts_qs)

            random.shuffle(executable_tweet)
            print(f"tweet_ids: {executable_tweet}\n")
            if len(executable_tweet):
                tweet_id = executable_tweet[0]
            else:
                continue
            print(f"Like action on tweet_id: {tweet_id}\n")
            like_count = 0
            for acc in twitter_accounts_qs:
                print(f"Account: {acc.screen_name}, id: {acc.id}")
                if like_count >= int(count):
                    break

                try:
                    """
                    Engagement module initialization
                    """
                    bot = TwitterAccountEngagement(
                        acc_id=acc.id,
                        target_username=target_username,
                        tweet_id=tweet_id,
                    )

                    """
                    Follow Action
                    """
                    follow_job = TwitterActionLog.objects.filter(
                        twitter_account=acc,
                        target_id=bot.recent_tweet_id,
                        action_type="FOLLOW",
                    )
                    if (
                        not only_like
                        and random.choice([0, 0, 1, 0, 0])
                        and not follow_job.exists()
                    ):
                        time.sleep(random.randrange(200, 400))
                        follow_resp = bot.follow()

                        TwitterActionLog.objects.create(
                            twitter_account=acc,
                            action_type="FOLLOW",
                            target_id=bot.recent_tweet.user.id,
                            target_screen_name=bot.target_username,
                            api_response=follow_resp,
                        )
                        print("follow action completed")

                    """
                    Retweet Action
                    """
                    retweet_job = TwitterActionLog.objects.filter(
                        twitter_account=acc,
                        target_id=bot.recent_tweet_id,
                        action_type="RETWEET",
                    )
                    if (
                        not only_like
                        and random.choice([0, 0, 1, 0, 0])
                        and not retweet_job.exists()
                    ):
                        time.sleep(random.randrange(200, 400))
                        retweet_resp = bot.retweet_recent()

                        TwitterActionLog.objects.create(
                            twitter_account=acc,
                            action_type="RETWEET",
                            target_id=bot.recent_tweet_id,
                            target_screen_name=bot.target_username,
                            api_response=retweet_resp,
                        )
                        print("retweet action completed")

                    """
                    Comment Action
                    """
                    retweet_job = TwitterActionLog.objects.filter(
                        twitter_account=acc,
                        target_id=bot.recent_tweet_id,
                        action_type="COMMENT",
                    )
                    if (
                        not only_like
                        and random.choice([0, 0, 1, 0, 0])
                        and not retweet_job.exists()
                    ):
                        time.sleep(random.randrange(200, 400))
                        comments = TWITTER_COMMENTS
                        random.shuffle(comments)
                        random.shuffle(comments)
                        comment = random.choice(comments)
                        retweet_resp = bot.comment(comment)

                        TwitterActionLog.objects.create(
                            twitter_account=acc,
                            action_type="COMMENT",
                            target_id=bot.recent_tweet_id,
                            target_screen_name=bot.target_username,
                            api_response=retweet_resp,
                        )
                        print("comment action completed")

                    """
                    Like Action
                    """
                    like_job = TwitterActionLog.objects.filter(
                        twitter_account=acc,
                        target_id=bot.recent_tweet_id,
                        action_type="LIKE",
                    )
                    if not like_job.exists():
                        time.sleep(random.randrange(200, 400))
                        like_resp = bot.like(bot.recent_tweet_id)

                        TwitterActionLog.objects.create(
                            twitter_account=acc,
                            action_type="LIKE",
                            target_id=bot.recent_tweet.id,
                            target_screen_name=bot.target_username,
                            api_response=like_resp,
                        )
                        print("like action completed")
                        like_count += 1

                    time.sleep(random.randrange(200, 400))
                    print(
                        f"Account: {acc.screen_name} | Task executed successfully\n\n"
                    )

                except tweepy.TweepError as tweepy_error:
                    error = tweepy_error.reason
                    error_log = f"Account: {acc.screen_name},\n {error}"
                    print(error_log)

                    error_msg = error

                    if "This request looks like it might be automated" in error_msg:
                        acc.status = "INACTIVE"
                        acc.save()

                    elif (
                        "Your account is suspended and is not permitted to access this feature."
                        in error_msg
                    ):
                        acc.status = "INACTIVE"
                        acc.save()

                    else:
                        acc.status = "BANNED"
                        acc.save()

                    TwitterActionLog.objects.create(
                        twitter_account=acc,
                        action_type="TRACEBACK",
                        target_id=acc.screen_name,
                        target_screen_name=acc.screen_name,
                        api_response=error,
                    )
                    send_log(log_type="Twitter Engagement Error: ", error=error_log)
                    break
                except Exception as e:
                    error = traceback.format_exc()
                    error_log = f"Account: {acc.screen_name},\n error: {error}"
                    print(error_log)
                    if "To protect our users from spam" in error:
                        acc.status = "BANNED"
                        acc.save()
                    TwitterActionLog.objects.create(
                        twitter_account=acc,
                        action_type="TRACEBACK",
                        target_id=acc.screen_name,
                        target_screen_name=acc.screen_name,
                        api_response=error,
                    )
                    send_log(log_type="Twitter Engagement Error: ", error=error_log)
                    break
