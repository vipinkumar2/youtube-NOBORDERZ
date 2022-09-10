import json
import traceback

from twitterbot.utils import *
from twitterbot.constants import *
from twitterbot.models import *
from django.db.models import Q
from django.core.management.base import BaseCommand
from slack_logger import send_log


class Command(BaseCommand):
    help = "Update Twitter accounts profile with ART pictures"

    def get_twitter_accounts(self, account_type):
        exclude_ids = list(
            TwitterJob.objects.filter(
                job_type="UPDATE_ART_PROFILE", status="C"
            ).values_list("twitter_account_id", flat=True)
        )
        account_qs = list(
            TwitterAccount.objects.filter(
                access_key__isnull=False,
                access_secret__isnull=False,
                status="ACTIVE",
                account_type=account_type,
            ).filter(~Q(id__in=exclude_ids))
        )

        random.shuffle(account_qs)
        random.shuffle(account_qs)
        total_filtered_accounts = len(account_qs)
        print(f"Twitter Accounts found: {total_filtered_accounts}")
        return account_qs

    def create_job(self, account_id):
        twitter_account = TwitterAccount.objects.get(id=account_id)
        TwitterJob.objects.create(
            user=twitter_account.user,
            twitter_account=twitter_account,
            job_type="UPDATE_ART_PROFILE",
            status="C",
        )

    def add_arguments(self, parser):
        parser.add_argument(
            "--is_test",
            default=False,
            help="testing accounts only",
        )
        parser.add_argument(
            "--account_type",
            default=True,
            help="Target account type",
        )

    def get_random_wait(self, initial_limit=1, upper_limit=5):
        return random.randint(initial_limit, upper_limit)

    def handle(self, *args, **options):
        is_test = options.get("is_test")
        account_type = options.get("account_type")
        update_count = 0

        while True:
            if is_test:
                account_qs = TwitterAccount.objects.filter(
                    access_key__isnull=False,
                    access_secret__isnull=False,
                    status="TESTING",
                )
            else:
                account_qs = self.get_twitter_accounts(account_type)

            for account in account_qs[:1]:
                try:
                    print(f"Updating Twitter Account: {account.screen_name}\n")
                    this = UpdateTwitterAccount(account.id)
                    response = this.update_profile()
                    print(
                        f"twitter_account_id: {account.id} | screen_name: {account.screen_name} \
                    | Account updated successfully.\n\n"
                    )
                    self.create_job(account.id)
                    TwitterActionLog.objects.create(
                        twitter_account=account,
                        action_type="UPDATE_ART_PROFILE",
                        target_id=this.me.id,
                        target_screen_name=this.me.screen_name,
                        api_response=response,
                    )
                    update_count += 1
                    time.sleep(self.get_random_wait(initial_limit=150, upper_limit=200))
                except tweepy.TweepError as tweepy_error:
                    error = tweepy_error.reason
                    error_log = f"Account: {account.screen_name},\n {error}"
                    # print(error_log)
                    error_msg = json.loads(tweepy_error.reason.replace("'", '"'))[0][
                        "message"
                    ]

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

                    TwitterActionLog.objects.create(
                        twitter_account=account,
                        action_type="TRACEBACK",
                        target_id=account.screen_name,
                        target_screen_name=account.screen_name,
                        api_response=error,
                    )
                    send_log(
                        log_type="Twitter Account Updation Error: ", error=error_log
                    )
                    time.sleep(self.get_random_wait(initial_limit=250, upper_limit=300))
                except Exception as e:
                    error = traceback.format_exc()
                    error_log = f"Account: {account.screen_name}, error: {error}"
                    print(error_log)
                    if "To protect our users from spam" in error:
                        account.status = "BANNED"
                        account.save()
                    TwitterActionLog.objects.create(
                        twitter_account=account,
                        action_type="TRACEBACK",
                        target_id=account.screen_name,
                        target_screen_name=account.screen_name,
                        api_response=error,
                    )
                    send_log(
                        log_type="Twitter Account Updation Error: ", error=error_log
                    )
                    time.sleep(self.get_random_wait(initial_limit=150, upper_limit=200))
