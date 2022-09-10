from django.db import models
from core.models import User, TimeStampModel
from django.db.models import JSONField as JSONFieldPostgres
from django.contrib.postgres.fields import ArrayField


class TwitterAccount(TimeStampModel):
    ACC_TYPE = (
        ("ART", "ART"),
        ("XANALIA_NFT", "XANALIA_NFT"),
        ("MKT_MEDIA", "MKT_MEDIA")
    )

    STATUS = (
        ("ACTIVE", "ACTIVE"),
        ("TESTING", "TESTING"),
        ("INACTIVE", "INACTIVE"),
        ("BANNED", "BANNED"),
        ("SUSPENDED", "SUSPENDED")
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=STATUS, default="ACTIVE")
    email = models.EmailField(max_length=255, null=True, blank=True)
    screen_name = models.CharField(max_length=15, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    password = models.CharField(max_length=40, null=True, blank=True)
    country = models.CharField(max_length=40, null=True, blank=True)
    access_key = models.CharField(max_length=100, null=True, blank=True)
    access_secret = models.CharField(max_length=100, null=True, blank=True)
    consumer_key = models.CharField(max_length=100, null=True, blank=True)
    consumer_secret = models.CharField(max_length=100, null=True, blank=True)
    account_type = models.CharField(
        max_length=100, choices=ACC_TYPE, null=True, blank=True
    )

    def __str__(self):
        return self.screen_name


class TwitterUser(TimeStampModel):
    username = models.CharField(max_length=255, null=True, blank=True)
    screen_name = models.CharField(max_length=255, null=True, blank=True)


class TwitterGroup(TimeStampModel):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    desc = models.CharField(max_length=200, blank=True, null=True)


class CompetitorUserDetials(TimeStampModel):
    target_user = models.CharField(max_length=255, null=True, blank=True)
    followers = models.ManyToManyField(TwitterUser, related_name="followers")
    following = models.ManyToManyField(TwitterUser, related_name="following")


class TwitterJob(TimeStampModel):
    JOB_TYPE = (
        ("TWEET_TEXT", "TWEET_TEXT"),
        ("TWEET_IMAGE", "TWEET_IMAGE"),
        ("TWEET", "TWEET"),
        ("LIKE", "LIKE"),
        ("RETWEET", "RETWEET"),
        ("FOLLOW_SINGLE_USER", "FOLLOW_SINGLE_USER"),
        ("UNFOLLOW", "UNFOLLOW"),
        ("UPDATE_ART_PROFILE", "UPDATE_ART_PROFILE"),
        ("MULTIPLE_FOLLOW", "MULTIPLE_FOLLOW"),
    )
    JOB_STATUS = (
        ("P", "PENDING"),
        ("C", "COMPLETED"),
        ("F", "FAILED"),
        ("I", "In-progress"),
        ("CN", "CANCELED"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    twitter_account = models.ForeignKey(
        TwitterAccount, blank=True, null=True, on_delete=models.CASCADE
    )
    job_type = models.CharField(max_length=100, choices=JOB_TYPE)
    target_username = models.ManyToManyField(
        TwitterUser, related_name="target_insta_users"
    )
    status = models.CharField(max_length=2, choices=JOB_STATUS, blank=True, null=True)
    tweet_id = models.CharField(max_length=255, blank=True, null=True)
    image_path = models.CharField(max_length=255, blank=True, null=True)
    text_message = models.CharField(max_length=255, blank=True, null=True)
    follow_user = models.CharField(max_length=100, null=True, blank=True)
    last_error = models.TextField(null=True, blank=True)


class TwitterActionLog(TimeStampModel):
    ACTION_TYPE = (
        ("LIKE", "LIKE"),
        ("TWEET", "TWEET"),
        ("FOLLOW", "FOLLOW"),
        ("UNFOLLOW", "UNFOLLOW"),
        ("TWEET_TEXT", "TWEET_TEXT"),
        ("TWEET_IMAGE", "TWEET_IMAGE"),
        ("RETWEET", "RETWEET"),
        ("COMMENT", "COMMENT"),
        ("MEDIA_POST", "MEDIA_POST")
    )

    twitter_account = models.ForeignKey(
        TwitterAccount, blank=True, null=True, on_delete=models.CASCADE
    )
    action_type = models.CharField(
        max_length=32, choices=ACTION_TYPE, blank=True, null=True
    )
    target_id = models.CharField(max_length=100, null=True, blank=True)
    target_screen_name = models.CharField(max_length=100, null=True, blank=True)
    api_response = JSONFieldPostgres(default=dict, blank=True, null=True)


class Tweet(TimeStampModel):
    tweet_id = models.CharField(max_length=100, unique=True)
    text = models.CharField(max_length=1000, null=True, blank=True)
    image = ArrayField(models.CharField(max_length = 500, default = " "), null = True, blank = True)
    tweeted = models.BooleanField(default=False)
    tweet_meta = JSONFieldPostgres(default=dict, blank=True, null=True)
    video = ArrayField(models.CharField(max_length = 500, default = " "), null = True, blank = True)
    likes = models.CharField(max_length=50, null=True, blank=True)
    retweet = models.CharField(max_length=50, null=True, blank=True)
    screen_name = models.CharField(max_length=50, null=True, blank=True)
    status = models.BooleanField(default=False)


