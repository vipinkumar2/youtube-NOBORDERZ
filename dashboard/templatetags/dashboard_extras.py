import datetime
from django import template
from membership.models import Subscription
from core.models import User
from dateutil.relativedelta import relativedelta
import pytz

register = template.Library()


def to_string(value):
    return str(value)


def exists(filter):
    return True if filter.exists() else False


def is_subscribed(user):
    if user.user_type == "user":
        subscription_exists = Subscription.objects.filter(
            user=user, is_active=True
        ).exists()
        acc_created = user.created + datetime.timedelta(days=2)
        if subscription_exists or acc_created.date() >= datetime.datetime.now().date():
            return True
    else:
        return True


def is_email_verified(user):
    if user.user_type == "user":
        return User.objects.filter(id=user.id, email_verified=True).exists()
    else:
        return True


def subscription_expire_date(self, user):
    subs = Subscription.objects.filter(user=user, is_active=True).order_by("-created")
    if user.user_type.lower() == "user" and subs.exists():
        subscription = subs.last()
        plan = subscription.plan
        created = subscription.created
        if plan.plan_type == "month":
            date = created + relativedelta(months=1)
        elif plan.plan_type == "year":
            date = created + relativedelta(years=1)
        else:
            date = created + datetime.timedelta(days=2)
        expire = date.strftime("%Y-%m-%d")
        return expire
    else:
        created = user.created
        date = created + datetime.timedelta(days=2)
        return date.strftime("%Y-%m-%d")


def get_about(user_account):
    return user_account.data.get("account_data")


def tag_split(compitator):
    try:
        data = compitator.split(",")
    except:
        data = []
    return data


def scheduled_for(self, job):
    tz = job.timezone if job.timezone else "UTC"
    sctz = job.scheduled_for
    try:
        scheduled_time = sctz.astimezone(pytz.timezone(tz))
    except:
        scheduled_time = sctz

    return datetime.datetime.strftime(scheduled_time, "%Y-%B-%d %H:%M")


register.filter("to_string", to_string)
register.filter("get_about", get_about)
register.filter("is_subscribed", is_subscribed)
register.filter("is_email_verified", is_email_verified)
register.filter("exists", exists)
register.filter("subscription_expire_date", subscription_expire_date)
register.filter("tag_split", tag_split)
register.filter("scheduled_for", scheduled_for)
