import datetime
from django_cron import CronJobBase, Schedule
from membership.models import Subscription
from dateutil.relativedelta import relativedelta


class CheckSubscription(CronJobBase):
    RUN_EVERY_MINS = 1440  # everyday
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "quick.CheckSubscription"

    def do(self):
        subscriptions = Subscription.objects.filter(is_active=True)
        for subscription in subscriptions:
            created = subscription.created
            expire = None
            if subscription.plan.plan_type == "month":
                expire = created + relativedelta(months=1)
            elif subscription.plan.plan_type == "year":
                expire = created + relativedelta(years=1)

            if expire and expire.date() <= datetime.datetime.now().date():
                subscription.is_active = False
                subscription.save()
