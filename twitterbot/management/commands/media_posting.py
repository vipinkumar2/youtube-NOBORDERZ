import os
import time
import random
import tweepy
import requests
import traceback

from twitterbot.utils import *
from twitterbot.models import *
from django.core.management.base import BaseCommand, CommandError
from twitterbot.proxy import get_proxies, get_proxy


class Command(BaseCommand):
    help = "Marketing Media Posting Script"

    def send_logs(self, text):
        data = {"text": text}
        response = requests.post(
            url="https://hooks.slack.com/services/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I",
            json=data,
        )

        print(response.text)
        return True

    def handle(self, *args, **options):
        # for i in range(5):

        mapo = MediaAccountPosting()

        success_count = 0
        failed_count = 0

        for acc in mapo.media_accounts:
            acc = TwitterAccount.objects.get(id=acc.id)
            print(acc, acc.status)
            if acc.status == "ACTIVE":

                # get text/media from AI
                tweet_text = "HAPPY NATIONAL EMPANADA DAY!"
                tweet_media_path = "/home/angelium/Downloads/media_testing.jpg"

                api = mapo.get_api(acc_id=acc.id)

                try:
                    action_resp = mapo.make_post(api, tweet_text, tweet_media_path)

                    TwitterActionLog.objects.create(
                        twitter_account=acc,
                        action_type="MEDIA_POST",
                        api_response=action_resp,
                    )

                    print(
                        f"Successfully Posted on {acc.screen_name}| Text: {tweet_text} ||| Media_Path: {tweet_media_path} |"
                    )

                    success_count += 1

                except tweepy.error.TweepError:
                    account = TwitterAccount.objects.filter(id=acc.id)[0]
                    error = traceback.format_exc()
                    error_log = f"Account: {acc.screen_name}, error: {error}"
                    print(error_log)

                    if "This request looks like it might be automated" in error:
                        account.status = "INACTIVE"
                        account.save()

                    elif (
                        "Your account is suspended and is not permitted to access this feature."
                        in error
                    ):
                        account.status = "INACTIVE"
                        account.save()

                    else:
                        account.status = "BANNED"
                        account.save()

                    TwitterActionLog.objects.create(
                        twitter_account=acc,
                        action_type="TRACEBACK",
                        api_response=error,
                    )

                    failed_count += 1

                rand_time = random.randrange(2600, 3000)
                print(f"Sleeping For {rand_time/60} minutes!")
                time.sleep(rand_time)

        msg = f"""
        *******************
        MEDIA POSTING STATS
        *******************

        Completed: {success_count}
        Failed: {failed_count}
        """
        self.send_logs(msg)
