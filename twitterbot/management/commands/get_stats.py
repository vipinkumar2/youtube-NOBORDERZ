import csv
import sys
import datetime
import requests

from django.core.management.base import BaseCommand, CommandError
from twitterbot.models import *


class Command(BaseCommand):
    help = "Get stats"

    def add_arguments(self, parser):
        parser.add_argument(
            "--channel",
            default=False,
            help="For which channel",
        )

        parser.add_argument(
            "--stat_type",
            default=False,
            help="target username for twitter engagement.",
        )

    def send_logs(self, text):
        data = {"text": text}
        response = requests.post(
            url="https://hooks.slack.com/services/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",
            json=data,
        )

        print(response.text)
        return True

    def handle(self, *app_labels, **options):
        channel = options.get("channel")
        stat_type = options.get("stat_type")

        if channel == "dev_surviral" and stat_type == "twitter_engagement":
            engagement_logs_today = TwitterActionLog.objects.filter(
                created__date__gte=datetime.datetime.today()
            ).exclude(twitter_account__account_type="MKT_MEDIA")
            likes = engagement_logs_today.filter(action_type="LIKE").count()
            comments = engagement_logs_today.filter(action_type="COMMENT").count()
            follows = engagement_logs_today.filter(action_type="FOLLOW").count()
            retweets = engagement_logs_today.filter(action_type="RETWEET").count()

            msg = f"""
                    ***********************************************
                    Twitter Account Engagement Stats
                    ***********************************************
                    Likes : {likes}
                    Comments : {comments} 
                    Follows : {follows}
                    Retweets : {retweets}
                    ***********************************************
                    """

            self.send_logs(msg)

        elif channel == "mkt_media" and stat_type == "media_posting":
            media_logs_today = TwitterActionLog.objects.filter(
                created__date__gte=datetime.datetime.today()
            ).exclude(twitter_account__account_type__in=["ART", "XANALIA_NFT"])

            successfull_count = media_logs_today.filter(
                action_type="MEDIA_POST"
            ).count()
            failed_count = media_logs_today.filter(action_type="TRACEBACK").count()
