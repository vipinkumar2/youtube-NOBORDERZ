import traceback
from twitterbot.utils import *
from twitterbot.constants import *
from twitterbot.models import *
from django.db.models import Q
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Scrape Tweet data and save in database if like greater then 1000"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tags",
            default=False,
            help="Screen name to scrape tweet data",
        )

    def handle(self, *args, **options):
        tags = options.get("tags")

        if tags:
            try:
                scrape = ScrapeTweet()
                scrape_data = scrape.save_tweet_data(tags)
                if scrape_data:
                    print("Scrape Tweet method finished")

            except Exception as ex:
                error = traceback.format_exc()
                print(error)
                print(f"Something went wrong exception is -------------{ex.__dict__}")
        else:
            print("No screen name found !")
