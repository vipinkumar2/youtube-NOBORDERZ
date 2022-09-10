import logging
from decimal import Decimal

import stripe
from django.conf import settings

from membership.models import (
    StripeCustomer,
    StripeCustomerCard,
    Subscription,
    StripeTransactionHistory,
)

stripe.api_key = settings.STRIPE_SECRET_KEY

STRIPE_COUNTRY_CODE = {
    "AUSTRALIA": "AU",
    "AUSTRIA": "AT",
    "BELGIUM": "BE",
    "BRAZIL ": "BR",
    "CANADA": "CA",
    "DENMARK": "DK",
    "FINLAND": "FI",
    "FRANCE": "FR",
    "GERMANY": "DE",
    "HONG KONG": "HK",
    "INDIA": "IN",
    "IRELAND": "IE",
    "JAPAN": "JP",
    "LUXEMBOURG": "LU",
    "MEXICO ": "MX",
    "NETHERLANDS": "NL",
    "NEW ZEALAND": "NZ",
    "NORWAY": "NO",
    "SINGAPORE": "SG",
    "SPAIN": "ES",
    "SWEDEN": "SE",
    "SWITZERLAND": "CH",
    "UNITED KINGDOM": "GB",
    "UNITED STATES": "US",
    "ITALY": "IT",
    "PORTUGAL": "PT",
}


def create_stripe_customer(user, line1, country):
    created_stripe_token = ""
    try:
        country_code = STRIPE_COUNTRY_CODE.get(country)
        if not country_code:
            country_code = "JP"
        address = {
            "line1": line1,
            "postal_code": "190-0100",
            "city": "San Francisco",
            "state": "CA",
            "country": country_code,
        }
        response = stripe.Customer.create(
            name=user.username,
            email=user.email,
            address=address,
            description="User created for the surviral web payment",
        )
        created_stripe_token = response.id
        StripeCustomer.objects.create(
            user=user, stripe_customer_id=created_stripe_token
        )
        logging.info(
            "=====================Create stripe customer success=============================="
        )
        logging.info("Successfully created")
        print("Done")
    except Exception as ex:
        logging.info(
            "=====================Create stripe customer Error=============================="
        )
        logging.info(str(ex))
        print(ex)
        return created_stripe_token
    return created_stripe_token


def retrive_stripe_customer(stripe_token):
    retrieve_stripe_token = ""
    try:
        response = stripe.Customer.retrieve(stripe_token)
        retrieve_stripe_token = response.id
        logging.info(
            "=====================Retrive stripe customer success=============================="
        )
        logging.info("Successfully Retrived")
    except Exception as ex:
        logging.info(
            "=====================Retrive stripe customer Error=============================="
        )
        logging.info(str(ex))
        return retrieve_stripe_token
    return retrieve_stripe_token


def retrive_customer_cards(customer):
    response = stripe.Customer.list_sources(customer, object="card")
    return response


def remove_customer_cards(customer, card):
    stripe.Customer.delete_source(customer, card)
    return True


def create_card_token(number="4242424242424242", exp_month=4, exp_year=2021, cvc="123"):
    response = stripe.Token.create(
        card={
            "number": number,
            "exp_month": exp_month,
            "exp_year": exp_year,
            "cvc": cvc,
        },
    )
    return response.id


def assign_source_to_customer(stripe_user, source, is_default=True):
    response = stripe.Customer.create_source(
        stripe_user.stripe_customer_id, source=source
    )
    if response:
        user_card = StripeCustomerCard.objects.create(
            is_default=is_default,
            stripe_customer=stripe_user,
            stripe_card_id=response.id,
            last_four=response.last4,
            brand=response.brand,
            exp_month=response.exp_month,
            exp_year=response.exp_year,
        )
    return response.id


def save_payment_history(user, amount, subscription_id):
    history = StripeTransactionHistory.objects.create(
        user=user,
        stripe_customer=user.stripe_user,
        stripe_token_charge=subscription_id,
        amount=amount,
    )
    return history


def update_customer_card_address(stripe_user, card, address):
    if stripe_user.stripe_user_cards.filter(stripe_card_id=card):
        customer_card = stripe_user.stripe_user_cards.filter(
            stripe_card_id=card
        ).first()
        customer_card.name = address["name"]
        customer_card.state = address["state"]
        customer_card.country = address["country"]
        customer_card.address = address["address"]
        customer_card.save()
        return customer_card
    return ""


def create_stripe_plan(plan_name, interval, amount, is_active):
    product = stripe.Product.create(name=plan_name)
    plan = stripe.Plan.create(
        amount_decimal=round(float(amount) * 100),
        currency="USD",
        interval=interval,
        product=product.id,
        active=is_active,
    )
    return (product.id, plan.id)


def update_stripe_plan(plan_id, amount, is_active):
    stripe.Plan.modify(plan_id, active=is_active)
    return ""


def subscribe_stripe_user(plan, stripe_customer, user):
    response = stripe.Subscription.create(
        customer=stripe_customer.stripe_customer_id,
        items=[
            {"price": plan.stripe_plan_id},
        ],
    )
    if response:
        user_card = Subscription.objects.create(
            plan=plan, user=user, stripe_subscription_id=response.id
        )
    return response.id
