from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import signals

from core.models import TimeStampModel
from decimal import *


User = get_user_model()


class Plan(TimeStampModel):
    PLAN_TYPE = (
        ("month", "month"),
        ("year", "year"),
    )
    name = models.CharField(max_length=50, unique=True)
    plan_type = models.CharField(max_length=50, choices=PLAN_TYPE, default="month")
    amount = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    stripe_plan_id = models.CharField(max_length=250, null=True, blank=True)
    stripe_product_id = models.CharField(max_length=250, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class StripeCustomer(TimeStampModel):
    user = models.OneToOneField(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="stripe_user",
    )
    stripe_customer_id = models.CharField(max_length=150, unique=True)
    last_subscription_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class Subscription(TimeStampModel):
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="subscriber",
    )
    plan = models.ForeignKey(
        Plan,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="subscription_plan",
    )
    stripe_subscription_id = models.CharField(
        max_length=150, blank=True, null=True, default=None
    )
    is_active = models.BooleanField(default=True)
    end_date = models.DateTimeField(blank=True, null=True)


class StripeCustomerCard(TimeStampModel):
    stripe_customer = models.ForeignKey(
        StripeCustomer, on_delete=models.CASCADE, related_name="stripe_user_cards"
    )
    stripe_card_id = models.CharField(max_length=150, unique=True)
    last_four = models.CharField(max_length=40)
    brand = models.CharField(max_length=40)
    exp_month = models.IntegerField()
    exp_year = models.IntegerField()
    is_default = models.BooleanField(default=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    id_deleted = models.BooleanField(default=False)

    def __str__(self):
        return (
            self.stripe_customer.user.username
            if self.stripe_customer.user
            else self.stripe_customer
        )


class StripeTransactionHistory(TimeStampModel):
    # TODO add json field for request and response
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="stripe_transaction_user",
    )
    stripe_customer = models.ForeignKey(
        StripeCustomer,
        on_delete=models.CASCADE,
        related_name="stripe_customer_transactions",
    )
    amount = models.DecimalField(max_digits=50, decimal_places=10, default=0)
    stripe_token_charge = models.CharField(max_length=150, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    is_failed = models.BooleanField(default=False)

    def __str__(self):
        return self.stripe_customer.stripe_customer_id


def stripe_plan(sender, instance, signal, created=False, *args, **kwargs):
    from membership.utils import create_stripe_plan, update_stripe_plan

    if instance.stripe_plan_id:
        update_stripe_plan(instance.stripe_plan_id, instance.amount, instance.is_active)
    else:
        product_id, plan_id = create_stripe_plan(
            instance.name, instance.plan_type, instance.amount, instance.is_active
        )
        plans = Plan.objects.filter(pk=instance.id)
        plans.update(stripe_product_id=product_id, stripe_plan_id=plan_id)


signals.post_save.connect(stripe_plan, sender=Plan)
