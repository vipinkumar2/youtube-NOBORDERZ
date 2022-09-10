import time
import logging
import tweepy
import random
from background_task import background
from twitterbot.models import (
    TwitterAccount,
    TwitterJob,
    TwitterUser,
    CompetitorUserDetials,
)
from twitterbot.auth import get_auth
from django.conf import settings

CONSUMER_KEY = settings.CONSUMER_KEY
CONSUMER_SECRET = settings.CONSUMER_SECRET
ACCESS_KEY = settings.ACCESS_KEY
ACCESS_SECRET = settings.ACCESS_SECRET


@background(queue="twitter_job")
def user_follow(job_id, follewrs):
    jobs = TwitterJob.objects.get(id=job_id)
    jobs.status = "I"
    jobs.save()
    try:
        users = TwitterAccount.objects.filter(id=jobs.accounts.id).first()
        api = get_auth(
            users.cunsumer_key,
            users.cunsumer_secret,
            users.access_key,
            users.access_secret,
        )
        screen_name = api.get_user(follewrs).name
        if not api.get_user(follewrs).following:
            api.create_friendship(follewrs)
            obj = TwitterUser.objects.get_or_create(
                username=follewrs, screen_name=screen_name
            )
            jobs.status = "C"
            jobs.username.add(obj)
            jobs.save()
            logging.info(
                "===================== user follow successfully=============================="
            )
    except Exception as e:
        logging.info(e)
        jobs.status = "F"
        jobs.save()


@background(queue="twitter_job")
def multiple_user_follow(job_id, follewrs, number_of_follow):
    jobs = TwitterJob.objects.get(id=job_id)
    jobs.status = "I"
    jobs.save()
    try:
        users = TwitterAccount.objects.filter(id=jobs.accounts.id).first()
        api = get_auth(
            users.cunsumer_key,
            users.cunsumer_secret,
            users.access_key,
            users.access_secret,
        )
        ids = api.followers_ids(follewrs)
        random.shuffle(ids)
        follow_id = []
        for user_id in ids:
            if not api.get_user(user_id=user_id).following:
                follow_id.append(user_id)
                if len(follow_id) == number_of_follow:
                    break

        if number_of_follow < len(ids):
            for user_ids in follow_id:
                username = api.get_user(user_id=user_ids).screen_name
                screen_name = api.get_user(user_id=user_ids).name
                time.sleep(random.randint(0, 222))
                if not api.get_user(user_id=user_ids).following:
                    api.create_friendship(user_ids)
                    user, new = CompetitorUserDetials.objects.get_or_create(
                        target_user=follewrs
                    )
                    obj = TwitterUser.objects.create(
                        username=username, screen_name=screen_name
                    )
                    if user:
                        user.followers.add(obj)
                        user.save()
                    else:
                        new.followers.add(obj)
                        new.save()

                logging.info(
                    "===================== user follow successfully =============================="
                )
                print("user follow successfully")
            jobs.status = "C"
            jobs.save()
        else:
            jobs.status = "F"
            jobs.save()
    except Exception as e:
        logging.info(e)
        jobs.status = "F"
        jobs.save()


@background(queue="twitter_job")
def retweet_user_followers(job_id, follewrs, number_of_follow):
    jobs = TwitterJob.objects.get(id=job_id)
    jobs.status = "I"
    jobs.save()
    try:
        users = TwitterAccount.objects.filter(id=jobs.accounts.id).first()
        api = get_auth(
            users.cunsumer_key,
            users.cunsumer_secret,
            users.access_key,
            users.access_secret,
        )
        ids = api.followers_ids(follewrs)
        random.shuffle(ids)
        follow_id = []
        tweet_ids = []
        for user_id in ids:
            try:
                new_tweet_ids = api.user_timeline(
                    user_id=user_id, tweet_mode="extended"
                )
            except:
                new_tweet_ids = None
            if new_tweet_ids:
                status = api.get_status(new_tweet_ids[0].id)
                if not status.retweeted:
                    follow_id.append(user_id)
                    tweet_ids.append(new_tweet_ids[0].id)
                    if len(follow_id) == number_of_follow:
                        break
        if number_of_follow < len(ids):
            for user_id, tweet_id in zip(follow_id, tweet_ids):
                username = api.get_user(user_id=user_id).screen_name
                screen_name = api.get_user(user_id=user_id).name
                obj = TwitterUser.objects.create(
                    username=username, screen_name=screen_name, tweet_id=tweet_id
                )
                time.sleep(random.randint(0, 222))
                api.retweet(tweet_id)
                jobs.username.add(obj)
                jobs.save()
                logging.info(
                    "===================== retweet successfully=============================="
                )
            jobs.status = "C"
            jobs.save()
        else:
            jobs.status = "F"
            jobs.save()
    except Exception as e:
        logging.info(e)
        jobs.status = "F"
        jobs.save()


@background(queue="twitter_job")
def get_followers(target_users):
    try:
        api = get_auth(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
        follower = api.followers(target_users)
        random.shuffle(follower)
        for users in follower:
            print(users)
            user, _ = CompetitorUserDetials.objects.get_or_create(
                target_user=target_users
            )
            obj = TwitterUser.objects.create(
                username=users.screen_name, screen_name=users.name
            )
            user.followers.add(obj)
            user.save()

            logging.info(
                "===================== get followers =============================="
            )
        print("get user followers successfully")
    except Exception as e:
        logging.info(e)


@background(queue="twitter_job")
def get_following(target_users):
    try:
        api = get_auth(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
        follower = api.friends(target_users)
        random.shuffle(follower)
        for users in follower:
            user, _ = CompetitorUserDetials.objects.get_or_create(
                target_user=target_users
            )
            obj = TwitterUser.objects.create(
                username=users.screen_name, screen_name=users.name
            )
            user.following.add(obj)
            user.save()

            logging.info(
                "===================== get followers =============================="
            )
        print("get user followers successfully")
    except Exception as e:
        logging.info(e)
