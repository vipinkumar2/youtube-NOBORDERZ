import os
import random

from datetime import datetime
from core.models import User
from django.db.models import JSONField as JSONFieldPostgres
from django.db import models
import constants


class TimeStampModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def path_and_rename(instance, filename):
    upload_to = ""
    name = filename.split(".")[-2]
    ext = filename.split(".")[-1]
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nums = random.randint(0000, 9999)
    filename = f"{name}_{instance.user.id}_{date}_{nums}.{ext}"
    return os.path.join(upload_to, filename)


class Phone(TimeStampModel):
    PHONE_STATUS = (("ACTIVE", "ACTIVE"), ("INACTIVE", "INACTIVE"))
    phone_id = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    service = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, choices=PHONE_STATUS)
    resp_data = JSONFieldPostgres(default=dict, blank=True, null=True)


class SurviralGroup(TimeStampModel):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    desc = models.CharField(max_length=200, blank=True, null=True)


class UserAccount(TimeStampModel):
    ACC_TYPE = (("IG", "INSTAGRAM"), ("YT", "YOUTUBE"))

    GENDER_TYPE = (("M", "Male"), ("F", "Female"), ("B", "Both"))

    AUTH_TYPE = (("CO", "COMPANY"), ("CL", "CLIENT"))

    LOGIN_STATUS = (
        ("P", "PROCESSING"),
        ("IN", "LOGGED_IN"),
        ("OUT", "LOGGED_OUT"),
        ("F", "FAILED"),
        ("O", "OTP REQUIRED"),
    )

    ACC_STATUS = (("A", "Active"), ("I", "Inactive"), ("B", "Banned"))

    ACC_FOR = (("M", "Mobile"), ("W", "Web"))
    ENGAGE_FOR = (
        ("FZ", "FRONTIAZ"),
        ("JA", "JAPAN"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.ForeignKey(
        Phone,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="instagram_account_phone",
    )
    phone_country = models.CharField(
        max_length=100,
        choices=constants.SMS_COUNTRIES,
        blank=True,
        null=True,
        default="us",
    )
    account_type = models.CharField(max_length=2, choices=ACC_TYPE)
    auth_type = models.CharField(max_length=2, choices=AUTH_TYPE, default="CL")
    account_from = models.CharField(max_length=2, choices=AUTH_TYPE, default="CL")
    login_status = models.CharField(max_length=255, choices=LOGIN_STATUS, default="P")
    full_name = models.CharField(max_length=256, blank=True, null=True)
    account_username = models.CharField(max_length=256, unique=True)
    account_password = models.CharField(max_length=256)
    status = models.CharField(max_length=1, choices=ACC_STATUS)
    account_for = models.CharField(max_length=1, choices=ACC_FOR, default="W")
    engagement_for = models.CharField(
        max_length=50, choices=ENGAGE_FOR, default=None, blank=True, null=True
    )
    data = JSONFieldPostgres(default=dict, blank=True, null=True)
    followers_list = JSONFieldPostgres(default=dict, blank=True, null=True)
    earliest_post_detail = JSONFieldPostgres(default=dict, blank=True, null=True)
    perform_activity = models.BooleanField(default=False)
    target_auidience = models.TextField(null=True, blank=True)
    competitors = models.TextField(null=True, blank=True)
    target_area = models.CharField(max_length=256, blank=True, null=True)
    target_gender = models.CharField(
        max_length=2, choices=GENDER_TYPE, default="M", blank=True, null=True
    )
    country = models.CharField(max_length=150, blank=True, null=True)
    like = models.BooleanField(default=False)
    follow = models.BooleanField(default=False)
    unfollow = models.BooleanField(default=False)
    comment = models.BooleanField(default=False)
    automation = models.BooleanField(default=True)
    group = models.ForeignKey(
        SurviralGroup, blank=True, null=True, on_delete=models.SET_NULL
    )
    autodirectmessage = models.BooleanField(default=False)
    storydirectmessage = models.BooleanField(default=False)
    directmessage = models.TextField(null=True, blank=True)
    directmessagestory = models.TextField(null=True, blank=True)
    autoreply = models.BooleanField(default=False)
    story_dm_data = models.TextField(null=True, blank=True)
    twofa_protected = models.BooleanField(default=False)
    twofa_codes = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.account_username + " " + self.user.username + " " + self.status


class Device(TimeStampModel):
    DEVICE_STATUS = (("BZ", "BUSY"), ("SB", "STANDBY"))

    serial_no = models.CharField(max_length=96, blank=True, null=True)
    status = models.CharField(max_length=2, choices=DEVICE_STATUS)
    user_account_access = models.BooleanField(default=True)
    network_ip = models.CharField(max_length=54, blank=True, null=True, unique=True)
    accounts = models.ManyToManyField(UserAccount, blank=True, related_name="accounts")
    active_account = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="active_account",
    )
    data = JSONFieldPostgres(default=dict, blank=True, null=True)

    def __str__(self):
        return self.serial_no + " " + self.status


class Job(TimeStampModel):
    JOB_TYPE = (
        ("DM_2_FOLLOW_BK", "DM_2_FOLLOW_BK"),
        ("NEW_STORY_DIRECT_MESSAGE", "NEW_STORY_DIRECT_MESSAGE"),
        ("FOLLOW_BK_PERCENT", "FOLLOW_BK_PERCENT"),
        ("NEW_DIRECT_MESSAGE_STAT", "NEW_DIRECT_MESSAGE_STAT"),
        ("COLLECT_FOLO_FOLI", "COLLECT_FOLO_FOLI"),
        ("CMNT_TARGET_POST", "CMNT_TARGET_POST"),
        ("LIKE_CMNT_FOLI_POST", "LIKE_CMNT_FOLI_POST"),
        ("AUTO_REPLY_COMMENT", "AUTO_REPLY_COMMENT"),
        ("LIKE_CMNT_FOL_POST", "LIKE_CMNT_FOL_POST"),
        ("LIKE_COMMENT_POST", "LIKE_COMMENT_POST"),
        ("DM_2_FOLLOW_BK", "DM_2_FOLLOW_BK"),
        ("FOLLOW_COMP_FOLLOWERS", "FOLLOW_COMP_FOLLOWERS"),
        ("POST_STORY", "POST STORY"),
        ("ADVANCED_FOLLOW_TAGS", "ADVANCED_FOLLOW_TAGS"),
        ("POST", "POST"),
        ("POST_VIDEO", "POST VIDEO"),
        ("FEED_LIKE", "FEED_LIKE"),
        ("FEED_COMMENT", "FEED_COMMENT"),
        ("URL_LIKE_CMNT", "URL_LIKE_CMNT"),
        ("URL_LIKE_FOLLOW", "URL_LIKE_FOLLOW"),
        ("USERNAME_FOLLOW", "USERNAME_FOLLOW"),
        ("USERNAME_COMMENT", "USERNAME_COMMENT"),
        ("HASHTAG_FOLLOW", "HASHTAG_FOLLOW"),
        ("AUTO_LIKE", "AUTO_LIKE"),
        ("AUTO_COMMENT", "AUTO_COMMENT"),
        ("AUTO_FOLLOW", "AUTO_FOLLOW"),
        ("VIEW_STORY", "VIEW_STORY"),
        ("USERNAME_LIKE", "USERNAME_LIKE"),
        ("FOLLOW_USER", "FOLLOW_USER"),
        ("UNFOLLOW_USER", "UNFOLLOW_USER"),
        ("USERNAME_LIKE_FOLLOW", "USERNAME_LIKE_FOLLOW"),
        ("LOGIN_USER", "LOGIN_USER"),
        ("AUTO_UNFOLLOW", "AUTO_UNFOLLOW"),
        ("ENTER_OTP", "ENTER_OTP"),
        ("GET_PROFILE", "GET_PROFILE"),
        ("MULTI_USER_FOLLOW", "MULTI_USER_FOLLOW"),
        ("LIKE_MULTIPLE_POSTS", "LIKE_MULTIPLE_POSTS"),
        ("UNFOLLOW_SINGLE", "UNFOLLOW_SINGLE"),
        ("FOLLOW_TAGS", "FOLLOW_TAGS"),
        ("INSERT_INITIAL_POSTS", "INSERT_INITIAL_POSTS"),
        ("INSERT_RECENT_POSTS", "INSERT_RECENT_POSTS"),
        ("CREATE_BOT", "CREATE_BOT"),
        ("UPDATE_ENGAGEMENT_PROFILE", "UPDATE_ENGAGEMENT_PROFILE"),
        ("ENGAGEMENT_POST", "ENGAGEMENT_POST"),
        ("MULTI_IMAGE_POST", "MULTI_IMAGE_POST"),
        ("GET_STATS", "GET_STATS"),
    )

    APP_TYPE = (("IG", "INSTAGRAM"), ("YT", "YOUTUBE"))

    JOB_STATUS = (
        ("P", "PENDING"),
        ("C", "COMPLETED"),
        ("F", "FAILED"),
        ("I", "In-progress"),
        ("CN", "CANCELED"),
    )

    VPN = (
        ("SURF_SHARK", "SURF_SHARK"),
        ("VPN_CITY", "VPN_CITY"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_account = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, blank=True, null=True
    )
    job_type = models.CharField(max_length=100, choices=JOB_TYPE)
    job_title = models.CharField(max_length=100)
    app_type = models.CharField(max_length=2, choices=APP_TYPE)
    image = models.ImageField(upload_to=path_and_rename, blank=True, null=True)
    video = models.FileField(upload_to=path_and_rename, blank=True, null=True)
    scheduled_for = models.DateTimeField(
        auto_now_add=False, auto_now=False, blank=True, null=True
    )
    status = models.CharField(max_length=2, choices=JOB_STATUS, blank=True, null=True)
    is_directed = models.BooleanField(default=True)
    timezone = models.CharField(max_length=100, blank=True, null=True)
    data = JSONFieldPostgres(default=dict, blank=True, null=True)
    result_data = JSONFieldPostgres(default=dict, blank=True, null=True)
    is_draft = models.BooleanField(default=False)
    like_comment = models.BooleanField(default=False)
    other_acc_not_followed_back = models.BooleanField(default=False)
    other_acc_followed_back = models.BooleanField(default=False)
    vpn = models.CharField(max_length=100, choices=VPN, default="SURF_SHARK")

    def __str__(self):
        return self.job_title


class JobQueue(TimeStampModel):
    JOB_QUEUE_STATUS = (
        ("P", "PENDING"),
        ("C", "COMPLETED"),
        ("F", "FAILED"),
        ("I", "In-progress"),
        ("CN", "CANCELED"),
    )

    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=JOB_QUEUE_STATUS)

    def __str__(self):
        return (
            self.status
            + " "
            + self.job.job_type
            + " "
            + self.device.active_account.account_username
            if (self.device and self.device.active_account)
            else ""
        )


class UserPostsDetail(TimeStampModel):
    user_account = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    post = models.ForeignKey(Job, on_delete=models.CASCADE)
    likes_till_now = models.IntegerField(default=0)
    comments_till_now = models.IntegerField(default=0)

    def __str__(self):
        return self.post.job_title


class AccountStat(TimeStampModel):
    user_account = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    data = JSONFieldPostgres(default=dict, blank=True, null=True)
    profile_pic = models.URLField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.user_account.account_username


class ProfileHistory(models.Model):
    user_account = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    date_of_stat = models.DateTimeField(null=True, blank=True)
    data = JSONFieldPostgres(default=dict, blank=True, null=True)

    def __str__(self):
        return self.user_account.account_username + "_" + str(self.date_of_stat)


class HashtagsAndCompetitors(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hashtags = JSONFieldPostgres(default=dict, blank=True, null=True)
    competitors = JSONFieldPostgres(default=dict, blank=True, null=True)

    def __str__(self):
        return self.user.username


class Blog(TimeStampModel):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blog_posts"
    )
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=5000)
    image = models.ImageField(upload_to="", blank=True, null=True)

    def __str__(self):
        return f"{self.title}, {self.author}"


class AccountAnalytics(TimeStampModel):
    user_account = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, related_name="account_analytic"
    )
    day = models.IntegerField(default=0)
    followers = models.IntegerField(default=0)
    following = models.IntegerField(default=0)
    today_follow = models.IntegerField(default=0)
    today_follow_back = models.IntegerField(default=0)
    today_unfollow = models.IntegerField(default=0)
    today_profile_PV = models.IntegerField(default=0)
    today_post = models.IntegerField(default=0)
    today_story = models.IntegerField(default=0)
    today_save = models.IntegerField(default=0)
    today_like = models.IntegerField(default=0)
    today_comment = models.IntegerField(default=0)
    today_click = models.IntegerField(default=0)
    follow_back_per = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user_account.account_username}| Day: {self.created.day}"


class LikedCommentedAccounts(TimeStampModel):
    JOB_QUEUE_STATUS = (
        ("P", "PENDING"),
        ("C", "COMPLETED"),
        ("F", "FAILED"),
        ("I", "In-progress"),
        ("CN", "CANCELED"),
    )

    office_insta_account = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, blank=True, null=True
    )
    competitor_insta_username = models.CharField(max_length=50, null=True, blank=True)
    instagram_accounts = JSONFieldPostgres(blank=True, null=True)
    followed_insta_accounts = JSONFieldPostgres(blank=True, null=True)
    status = models.CharField(max_length=2, choices=JOB_QUEUE_STATUS, default="P")


class InstaAccFollowingsFollowers(TimeStampModel):
    office_insta_account = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, blank=True, null=True
    )
    recent_influencers = JSONFieldPostgres(blank=True, null=True)
    latest_followers = JSONFieldPostgres(blank=True, null=True)
    latest_followings = JSONFieldPostgres(blank=True, null=True)

    def __str__(self):
        return f"{self.office_insta_account.account_username}"


class UnfollowUsername(TimeStampModel):
    user_account = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    username = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.username}"


class FollowedUsername(TimeStampModel):
    user_account = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    username = models.CharField(max_length=150)

    def __str__(self):
        return f"followed: {self.username} by {self.user_account.account_username}"


class UserGoogleAccount(TimeStampModel):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=256)
    recovery_email = models.CharField(max_length=100)
    phone = models.ForeignKey(
        Phone,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="google_account_phone",
    )
    phone_country = models.CharField(max_length=100, blank=True, null=True)


class GoogleJobs(TimeStampModel):
    JOB_STATUS = (
        ("P", "PENDING"),
        ("C", "COMPLETED"),
        ("I", "In-progress"),
        ("F", "FAILED"),
    )
    firstname = models.CharField(max_length=100, null=True, blank=True)
    lastname = models.CharField(max_length=256, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=100, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=2, choices=JOB_STATUS, blank=True, null=True)


class DailyAccountData(TimeStampModel):
    user_account = models.ForeignKey(UserAccount, on_delete=models.CASCADE, null=True)
    cta = models.IntegerField(default=0)
    posts = models.IntegerField(default=0)
    unfollow = models.IntegerField(default=0)
    story_dm = models.IntegerField(default=0)
    followers = models.IntegerField(default=0)
    following = models.IntegerField(default=0)
    thank_u_dm = models.IntegerField(default=0)
    today_posts = models.IntegerField(default=0)
    comment_post = models.IntegerField(default=0)
    comment_follow = models.IntegerField(default=0)
    today_followers = models.IntegerField(default=0)
    today_followings = models.IntegerField(default=0)
    today_recieved_message_count = models.IntegerField(default=0)
    follow_bk_per = models.FloatField(null=True, blank=True, default=None)

    def store_daily_stats(
        self,
        user_account,
        cta,
        posts,
        unfollow,
        story_dm,
        followers,
        following,
        thank_u_dm,
        today_posts,
        comment_post,
        comment_follow,
        today_followers,
        today_followings,
        follow_bk_per,
    ):
        self.user_account = user_account
        self.cta = cta
        self.posts = posts
        self.unfollow = unfollow
        self.story_dm = story_dm
        self.followers = followers
        self.following = following
        self.thank_u_dm = thank_u_dm
        self.today_posts = today_posts
        self.comment_post = comment_post
        self.comment_follow = comment_follow
        self.today_followers = today_followers
        self.today_followings = today_followings
        self.follow_bk_per = follow_bk_per
        self.save()
