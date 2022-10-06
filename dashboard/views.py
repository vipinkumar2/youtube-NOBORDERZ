import os
import time
import boto3
import random
import pytz
import ast
import datetime
import json

import requests
from dateutil.parser import parse
from django.db.models import Q
from django.utils import timezone as tz
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from rest_framework.views import APIView
from rest_framework.response import Response
from membership import utils
from membership.models import Plan
from .forms import AddInstagramAccountForm
from django.contrib import messages
from instabot.models import (
    UserAccount,
    AccountStat,
    Job,
    Device,
    JobQueue,
    SurviralGroup,
    InstaAccFollowingsFollowers,
    DailyAccountData,
)
from youtubebot.models import YoutubeVideoUrl, YoutubeAccount, YoutubeJob, YoutubeGroup
from youtubebot.utils import (
    video_like,
    comment_on_video,
    subscribe_channel,
    video_dislike,      
    
    
    
    
    views_video,
    video_upload,
)
import constants
from django.utils import translation

from core.models import User
from youtubebot.tasks import *

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import google.oauth2.credentials

from google_auth_oauthlib.flow import InstalledAppFlow

URL = settings.INSTABOT_URL


def download_file_from_s3(file, file_path, bucket_name=None):
    if not bucket_name:
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    bucket_resource = s3

    bucket_resource.download_file(
        Bucket=bucket_name,
        Filename=file,
        Key=file_path,
    )


class HashtagsFollowView(TemplateView):
    template_name = "dashboard/tools/hashtags_follow.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_groups = SurviralGroup.objects.filter(user=user)
        context["user_groups"] = user_groups
        return context

    def post(self, request):
        scheduled_time = self.request.POST.get("scheduled_time")
        group = self.request.POST.get("group", None)
        insta_user_id = self.request.POST.get("insta_user_id")
        user = self.request.user
        timezone = self.request.POST.get("timezone", "Asia/Kolkata")
        hashtags = self.request.POST.get("hashtags")
        number_of_follows = self.request.POST.get("follows", 0)
        scheduled_for = parse(scheduled_time)
        scheduled_for = tz.make_aware(
            scheduled_for, pytz.timezone(self.request.user.timezone)
        )

        if group:
            group_accounts = UserAccount.objects.filter(group=group)
        else:
            group_accounts = None
        if group_accounts:
            for account in group_accounts:
                Job.objects.create(
                    user=user,
                    user_account=account,
                    job_type="HASHTAG_FOLLOW",
                    job_title="Follow {} accounts on basis of hashtag {}".format(
                        number_of_follows, hashtags
                    ),
                    app_type="IG",
                    scheduled_for=scheduled_for,
                    timezone=timezone,
                    status="P",
                    data={
                        "num_of_accounts_to_follow": number_of_follows,
                        "hashtag": hashtags,
                    },
                )

            messages.success(request, "Follow with hashtag Job created!")
            return render(request, self.template_name, self.get_context_data())

        else:
            account = UserAccount.objects.get(id=insta_user_id)
            Job.objects.create(
                user=user,
                user_account=account,
                job_type="HASHTAG_FOLLOW",
                job_title="Follow {} accounts on basis of hashtag {}".format(
                    number_of_follows, hashtags
                ),
                app_type="IG",
                scheduled_for=scheduled_for,
                timezone=timezone,
                status="P",
                data={
                    "num_of_accounts_to_follow": number_of_follows,
                    "hashtag": hashtags,
                },
            )

            messages.success(request, "Follow with hashtag Job created!")
            return render(request, self.template_name, self.get_context_data())


class AdvancedHashtagsFollowView(TemplateView):
    template_name = "dashboard/tools/advanced_hashtags_follow.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['user_accounts'] = self.request.user.useraccount_set.all()
        user = self.request.user
        user_groups = SurviralGroup.objects.filter(user=user)
        context["user_groups"] = user_groups
        return context

    def post(self, request):
        num_of_accounts_to_follow = 20
        scheduled_time = self.request.POST.get("scheduled_time")
        group = self.request.POST.get("group", None)
        url = URL + "advanced_follow_tags_accounts/"
        timezone = self.request.POST.get("timezone")

        if group:
            group_accounts = UserAccount.objects.filter(group=group)
        else:
            group_accounts = None
        if group_accounts:
            for account in group_accounts:
                data = {
                    "scheduled_time": scheduled_time,
                    "list_of_tags": self.request.POST.get("hashtags"),
                    "user_id": account.id,
                    "timezone": self.request.POST.get("timezone"),
                }

                try:
                    user_account = UserAccount.objects.get(id=account.id)
                    username, password = None, None

                    scheduled_for = parse(scheduled_time)
                    scheduled_for = tz.make_aware(
                        scheduled_for, pytz.timezone(timezone)
                    )
                    hashtag = data["list_of_tags"]

                    if hashtag and num_of_accounts_to_follow:
                        if user_account:
                            username = user_account.account_username
                            password = user_account.account_password

                    job = Job.objects.create(
                        user=user_account.user,
                        user_account=user_account,
                        job_type="ADVANCED_FOLLOW_TAGS",
                        job_title="Advanced Follow {} accounts on basis of hashtag {}".format(
                            num_of_accounts_to_follow, hashtag
                        ),
                        app_type="IG",
                        scheduled_for=scheduled_for,
                        timezone=data["timezone"],
                        status="P",
                        data={
                            "num_of_accounts_to_follow": num_of_accounts_to_follow,
                            "hashtag": hashtag,
                        },
                    )
                except Exception as e:
                    print(e)
                    messages.error(
                        request, "Advanced Follow with hashtag Job creation Failed!"
                    )
                    return render(request, self.template_name, self.get_context_data())

            messages.success(request, "Advanced Follow with hashtag Job created!")
            return render(request, self.template_name, self.get_context_data())

        else:
            data = {
                "scheduled_time": scheduled_time,
                "list_of_tags": self.request.POST.get("hashtags"),
                "user_id": self.request.POST.get("insta_user_id"),
                "timezone": self.request.POST.get("timezone"),
            }

            try:
                user_account = UserAccount.objects.get(id=data["user_id"])
                username, password = None, None

                scheduled_for = parse(scheduled_time)
                scheduled_for = tz.make_aware(scheduled_for, pytz.timezone(timezone))
                hashtag = data["list_of_tags"]

                if hashtag and num_of_accounts_to_follow:
                    if user_account:
                        username = user_account.account_username
                        password = user_account.account_password

                job = Job.objects.create(
                    user=user_account.user,
                    user_account=user_account,
                    job_type="ADVANCED_FOLLOW_TAGS",
                    job_title="Advanced Follow {} accounts on basis of hashtag {}".format(
                        num_of_accounts_to_follow, hashtag
                    ),
                    app_type="IG",
                    scheduled_for=scheduled_for,
                    timezone=data["timezone"],
                    status="P",
                    data={
                        "num_of_accounts_to_follow": num_of_accounts_to_follow,
                        "hashtag": hashtag,
                    },
                )

                messages.success(request, "Advanced Follow with hashtag Job created!")
                return render(request, self.template_name, self.get_context_data())
            except Exception as e:
                print(e)
                messages.error(
                    request, "Advanced Follow with hashtag Job creation Failed!"
                )
                return render(request, self.template_name, self.get_context_data())


class MultiUnfollowAPIView(TemplateView):
    template_name = "dashboard/tools/multiple_unfollow.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['user_accounts'] = self.request.user.useraccount_set.all()
        user = self.request.user
        user_groups = SurviralGroup.objects.filter(user=user)
        context["user_groups"] = user_groups
        return context

    def check_validity(self, acc):
        try:
            record = InstaAccFollowingsFollowers.objects.get(office_insta_account=acc)
            print(len(record.latest_followings["followings"]), "total followings")
            if len(record.latest_followings["followings"]) > 5000:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def post(self, request, *args, **kwargs):
        scheduled_time = self.request.POST.get("scheduled_time")
        limit = self.request.POST.get("number_Unfollower", 20)
        insta_user_id = self.request.POST.get("insta_user_id")
        timezone = self.request.POST.get("timezone")
        group = self.request.POST.get("group", None)
        user = self.request.user

        scheduled_for = parse(scheduled_time)
        scheduled_for = tz.make_aware(scheduled_for, pytz.timezone(timezone))
        if group:
            group_accounts = UserAccount.objects.filter(group=group)
        else:
            group_accounts = None
        if group_accounts:
            acc_list = []
            for account in group_accounts:
                if self.check_validity(account):
                    Job.objects.create(
                        user=user,
                        user_account=account,
                        job_type="AUTO_UNFOLLOW",
                        job_title="Unfollow Multiple Users",
                        app_type="IG",
                        scheduled_for=scheduled_for,
                        timezone=timezone,
                        status="P",
                        data={"times": limit},
                    )
                    acc_list.append(account.account_username)
            messages.success(
                request, "Multi UnFollow Job created for {}".format(acc_list)
            )
            return render(request, self.template_name, {})
        else:
            account = UserAccount.objects.get(id=insta_user_id)
            try:
                jobs = Job.objects.filter(
                    user_account=account,
                    job_type="AUTO_UNFOLLOW",
                    status__in=["P", "I"],
                )
            except Exception as e:
                jobs = None
            if jobs:
                messages.success(
                    request,
                    "Job Cannot Be Created, Please Wait for previous unfollow to finish",
                )
                return render(request, self.template_name, {})
            elif self.check_validity(account):
                Job.objects.create(
                    user=user,
                    user_account=account,
                    job_type="AUTO_UNFOLLOW",
                    job_title="Unfollow Multiple Users",
                    app_type="IG",
                    scheduled_for=scheduled_for,
                    timezone=timezone,
                    status="P",
                    data={"times": limit},
                )
                messages.success(request, "Multi UnFollow Job created!")
                return render(request, self.template_name, {})
            else:
                messages.info(
                    request,
                    "Multi UnFollow Job cannot be created for {}, may be he is having followings less than 5000".format(
                        account.account_username
                    ),
                )
                return render(request, self.template_name, {})


class HashTagsLikeView(TemplateView):
    template_name = "dashboard/tools/hashtags_like.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['user_accounts'] = self.request.user.useraccount_set.all()
        user = self.request.user
        user_groups = SurviralGroup.objects.filter(user=user)
        context["user_groups"] = user_groups
        return context

    def post(self, request, *args, **kwargs):
        group = self.request.POST.get("group", None)
        user = self.request.user
        hashtags = request.POST.get("hashtags")
        num_posts_like = request.POST.get("post_counts")
        timezone = self.request.POST.get("timezone")
        scheduled_for = datetime.datetime.now(pytz.UTC)

        if group:
            group_accounts = UserAccount.objects.filter(group=group)
        else:
            group_accounts = None
        if group_accounts:
            for account in group_accounts:
                if account.login_status == "IN":
                    Job.objects.create(
                        user=user,
                        user_account=account,
                        job_type="LIKE_MULTIPLE_POSTS",
                        job_title="Like Posts of {} hashtag".format(hashtags),
                        app_type="IG",
                        scheduled_for=scheduled_for,
                        timezone=timezone,
                        status="P",
                        data={"num_of_likes": num_posts_like, "hashtag": hashtags},
                    )

            messages.success(request, "Like with hashtag Job created!")
            return render(request, self.template_name, self.get_context_data())

        else:
            insta_user_id = self.request.POST.get("insta_user_id")
            account = UserAccount.objects.get(id=insta_user_id)
            Job.objects.create(
                user=user,
                user_account=account,
                job_type="LIKE_MULTIPLE_POSTS",
                job_title="Like Posts of {} hashtag".format(hashtags),
                app_type="IG",
                scheduled_for=scheduled_for,
                timezone=timezone,
                status="P",
                data={"num_of_likes": num_posts_like, "hashtag": hashtags},
            )

            messages.success(request, "Like with hashtag Job created!")
            return render(request, self.template_name, self.get_context_data())


class SingleFollowAPIView(TemplateView):
    template_name = "dashboard/tools/single_follow.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_groups = SurviralGroup.objects.filter(user=user)
        context["user_groups"] = user_groups
        return context

    def post(self, request, *args, **kwargs):
        target_user = self.request.POST.get("follow_username", None)
        user_id = self.request.POST.get("insta_user_id")
        timezone = self.request.POST.get("timezone", "Asia/Kolkata")
        user = self.request.user
        group = self.request.POST.get("group", None)
        scheduled_for = datetime.datetime.now(pytz.UTC)
        if group:
            group_accounts = UserAccount.objects.filter(group=group)
        else:
            group_accounts = None
        if group_accounts:
            for account in group_accounts:
                if account.login_status == "IN":
                    Job.objects.create(
                        user=user,
                        user_account=account,
                        job_type="USERNAME_FOLLOW",
                        job_title="Follow Single User",
                        app_type="IG",
                        timezone=timezone,
                        scheduled_for=scheduled_for,
                        status="P",
                        data={"target_user": target_user},
                    )
            messages.success(request, "Follow Job created!")
            return render(request, self.template_name, self.get_context_data())
        else:
            account = UserAccount.objects.get(id=user_id)
            Job.objects.create(
                user=user,
                user_account=account,
                job_type="USERNAME_FOLLOW",
                job_title="Follow Single User",
                app_type="IG",
                timezone=timezone,
                scheduled_for=scheduled_for,
                status="P",
                data={"target_user": target_user},
            )
            return render(request, self.template_name, self.get_context_data())


class LikeCmntOnPostAPIView(TemplateView):
    template_name = "dashboard/tools/like_cmnt.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_groups = SurviralGroup.objects.filter(user=user)
        context["user_groups"] = user_groups
        return context

    def post(self, request, *args, **kwargs):
        insta_user = self.request.POST.get("insta_username", None)
        lik_option = self.request.POST.get("like_post", None)
        cmnt_option = self.request.POST.get("cmnt_post", None)
        admin_id = self.request.POST.get("admin_user_id")
        user_account_id = self.request.POST.get("insta_user_id")
        timezone = self.request.POST.get("timezone")
        group = self.request.POST.get("group", None)
        user = self.request.user
        scheduled_for = datetime.datetime.now(pytz.UTC)

        # Create jobs for all accounts in a group
        if group:
            group_accounts = UserAccount.objects.filter(group=group)
        else:
            group_accounts = None
        if group_accounts:
            for account in group_accounts:
                if account.login_status == "IN":
                    Job.objects.create(
                        user=user,
                        user_account=account,
                        job_type="LIKE_COMMENT_POST",
                        job_title="Like or comment on post of target user",
                        app_type="IG",
                        image=None,
                        scheduled_for=scheduled_for,
                        timezone=timezone,
                        status="P",
                        data={
                            "target_username": insta_user,
                            "like": lik_option,
                            "comment": cmnt_option,
                        },
                    )

            messages.success(request, "Like or Comment on Post Job created!")
            return render(request, self.template_name, self.get_context_data())

        else:
            account = UserAccount.objects.get(id=user_account_id)
            Job.objects.create(
                user=user,
                user_account=account,
                job_type="LIKE_COMMENT_POST",
                job_title="Like or comment on post of target user",
                app_type="IG",
                image=None,
                scheduled_for=scheduled_for,
                timezone=timezone,
                status="P",
                data={
                    "target_username": insta_user,
                    "like": lik_option,
                    "comment": cmnt_option,
                },
            )
            messages.success(request, "Like or Comment on Post Job created!")
            return render(request, self.template_name, self.get_context_data())


class LikeCmntOnFollowingPostAPIView(TemplateView):
    template_name = "dashboard/tools/like_cmnt_followings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_groups = SurviralGroup.objects.filter(user=user)
        context["user_groups"] = user_groups
        return context

    def post(self, request, *args, **kwargs):
        insta_user = self.request.POST.get("insta_username", None)
        lik_option = self.request.POST.get("like_post", None)
        cmnt_option = self.request.POST.get("cmnt_post", None)
        admin_id = self.request.POST.get("admin_user_id")
        user_account_id = self.request.POST.get("insta_user_id")
        timezone = self.request.POST.get("timezone")
        group = self.request.POST.get("group", None)
        user = self.request.user
        scheduled_for = datetime.datetime.now(pytz.UTC)

        if group:
            group_accounts = UserAccount.objects.filter(group=group)
        else:
            group_accounts = None
        if group_accounts:
            for account in group_accounts:
                if account.login_status == "IN":
                    Job.objects.create(
                        user=user,
                        user_account=account,
                        job_type="LIKE_CMNT_FOL_POST",
                        job_title="Like or comment on post on followings of target user",
                        app_type="IG",
                        image=None,
                        scheduled_for=scheduled_for,
                        timezone=timezone,
                        status="P",
                        data={
                            "target_username": insta_user,
                            "like": lik_option,
                            "comment": cmnt_option,
                        },
                    )

        else:
            account = UserAccount.objects.get(id=user_account_id)
            Job.objects.create(
                user=user,
                user_account=account,
                job_type="LIKE_CMNT_FOL_POST",
                job_title="Like or comment on post on followings of target user",
                app_type="IG",
                image=None,
                scheduled_for=scheduled_for,
                timezone=timezone,
                status="P",
                data={
                    "target_username": insta_user,
                    "like": lik_option,
                    "comment": cmnt_option,
                },
            )

        messages.success(request, "Like or Comment on Followings Post Job created!")
        return render(request, self.template_name, self.get_context_data())


class LikeCmntOnFollowerPostAPIView(TemplateView):
    template_name = "dashboard/tools/like_cmnt_followers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_groups = SurviralGroup.objects.filter(user=user)
        context["user_groups"] = user_groups
        return context

    def post(self, request, *args, **kwargs):
        insta_user = self.request.POST.get("insta_username", None)
        lik_option = self.request.POST.get("like_post", None)
        cmnt_option = self.request.POST.get("cmnt_post", None)
        admin_id = self.request.POST.get("admin_user_id")
        user_account_id = self.request.POST.get("insta_user_id")
        timezone = self.request.POST.get("timezone")
        group = self.request.POST.get("group", None)
        user = self.request.user
        scheduled_for = datetime.datetime.now(pytz.UTC)

        if group:
            group_accounts = UserAccount.objects.filter(group=group)
        else:
            group_accounts = None
        if group_accounts:
            for account in group_accounts:
                if account.login_status == "IN":
                    Job.objects.create(
                        user=user,
                        user_account=account,
                        job_type="LIKE_CMNT_FOLI_POST",
                        job_title="Like or comment on post on followers of target user",
                        app_type="IG",
                        image=None,
                        scheduled_for=scheduled_for,
                        timezone=timezone,
                        status="P",
                        data={
                            "target_username": insta_user,
                            "like": lik_option,
                            "comment": cmnt_option,
                        },
                    )

        else:
            account = UserAccount.objects.get(id=user_account_id)
            Job.objects.create(
                user=user,
                user_account=account,
                job_type="LIKE_CMNT_FOLI_POST",
                job_title="Like or comment on post on followers of target user",
                app_type="IG",
                image=None,
                scheduled_for=scheduled_for,
                timezone=timezone,
                status="P",
                data={
                    "target_username": insta_user,
                    "like": lik_option,
                    "comment": cmnt_option,
                },
            )

        messages.success(request, "Like or Comment on Followings Post Job created!")
        return render(request, self.template_name, self.get_context_data())


class DirectMessageStatus(APIView):
    def get(self, request, *args, **kwargs):
        user_id = self.request.GET.get("insta_user_id", None)
        user_account = UserAccount.objects.get(id=user_id)
        return Response(
            {
                "success": True,
                "status": user_account.autodirectmessage,
                "message": user_account.directmessage,
            }
        )


class StoryDirectMessageStatus(APIView):
    def get(self, request, *args, **kwargs):
        user_id = self.request.GET.get("insta_user_id", None)
        user_account = UserAccount.objects.get(id=user_id)
        return Response(
            {
                "success": True,
                "status": user_account.storydirectmessage,
                "message": user_account.directmessagestory,
            }
        )


class AutoDirectMessageView(TemplateView):
    template_name = "dashboard/tools/auto_direct_message.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # user_account = UserAccount.objects.get(id=data['user_id'])
        # context['user_accounts'] = UserAccount.objects.filter()
        return context

    def post(self, request, *args, **kwargs):
        dm_status = self.request.POST.get("togBtn", None)
        user_id = self.request.POST.get("insta_user_id", None)
        message = self.request.POST.get("Message", None)
        user_account = UserAccount.objects.get(id=user_id)
        user_account.autodirectmessage = True if dm_status == "True" else False
        user_account.directmessage = message
        user_account.save()
        return render(request, self.template_name, {})


class StoryDirectMessageView(TemplateView):
    template_name = "dashboard/tools/story_dm.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # user_account = UserAccount.objects.get(id=data['user_id'])
        # context['user_accounts'] = UserAccount.objects.filter()
        return context

    def post(self, request, *args, **kwargs):
        dm_status = self.request.POST.get("togBtn", None)
        user_id = self.request.POST.get("insta_user_id", None)
        message = self.request.POST.get("Message", None)
        user_account = UserAccount.objects.get(id=user_id)
        user_account.storydirectmessage = True if dm_status == "True" else False
        user_account.directmessagestory = message
        user_account.save()
        return render(
            request,
            self.template_name,
            {"status": dm_status if dm_status == "True" else "False"},
        )


class ReplyCommentStatus(APIView):
    def get(self, request, *args, **kwargs):
        user_id = self.request.GET.get("insta_user_id", None)
        user_account = UserAccount.objects.get(id=user_id)
        return Response({"success": True, "status": user_account.autoreply})


class AutoReplyCommentView(TemplateView):
    template_name = "dashboard/tools/auto_reply.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # user_account = UserAccount.objects.get(id=data['user_id'])
        # context['user_accounts'] = UserAccount.objects.filter()
        return context

    def post(self, request, *args, **kwargs):
        dm_status = self.request.POST.get("togBtn", None)
        user_id = self.request.POST.get("insta_user_id", None)
        user_account = UserAccount.objects.get(id=user_id)
        user_account.autoreply = False if user_account.autoreply == True else True
        user_account.save()
        return render(request, self.template_name, {})


class GiveYourCmntAPIView(TemplateView):
    template_name = "dashboard/tools/manual_cmnt.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_groups = SurviralGroup.objects.filter(user=user)
        context["user_groups"] = user_groups
        return context

    def post(self, request, *args, **kwargs):
        insta_user = self.request.POST.get("insta_username", None)
        cmnt = self.request.POST.get("your_cmnt", None)
        admin_id = self.request.POST.get("admin_user_id")
        user_account_id = self.request.POST.get("insta_user_id")
        timezone = self.request.POST.get("timezone")
        group = self.request.POST.get("group", None)
        user = self.request.user
        scheduled_for = datetime.datetime.now(pytz.UTC)
        if group:
            group_accounts = UserAccount.objects.filter(group=group)
        else:
            group_accounts = None
        if group_accounts:
            for account in group_accounts:
                if account.login_status == "IN":
                    Job.objects.create(
                        user=user,
                        user_account=account,
                        job_type="CMNT_TARGET_POST",
                        job_title="Comment on post of target user",
                        app_type="IG",
                        image=None,
                        scheduled_for=scheduled_for,
                        timezone=timezone,
                        status="P",
                        data={"target_username": insta_user, "comment": cmnt},
                    )
        else:
            account = UserAccount.objects.get(id=user_account_id)
            Job.objects.create(
                user=user,
                user_account=account,
                job_type="CMNT_TARGET_POST",
                job_title="Comment on post of target user",
                app_type="IG",
                image=None,
                scheduled_for=scheduled_for,
                timezone=timezone,
                status="P",
                data={"target_username": insta_user, "comment": cmnt},
            )
        messages.success(request, "Like or Comment on Followings Post Job created!")
        return render(request, self.template_name, self.get_context_data())


class MultiFollowAPIView(TemplateView):
    template_name = "dashboard/tools/multiple_follow.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['user_accounts'] = self.request.user.useraccount_set.all()
        user = self.request.user
        user_groups = SurviralGroup.objects.filter(user=user)
        context["user_groups"] = user_groups
        return context

    def post(self, request, *args, **kwargs):
        removed_users = []
        target_user = self.request.POST.get("follow_multiple_users", None)
        target_user = target_user.split(",")
        number_of_followers = self.request.POST.get("number_of_followers")
        schedule_time = self.request.POST.get("scheduled_time")
        user_account_id = self.request.POST.get("insta_user_id")
        timezone = self.request.POST.get("timezone")
        """
        Check boxes
        """
        lik_cmnt_opt = True if self.request.POST.get("lk_cmnt_flw", None) else False
        not_followed_back = (
            True if self.request.POST.get("not_followed_back", None) else False
        )
        followed_back = True if self.request.POST.get("followed_back", None) else False
        group = self.request.POST.get("group", None)

        """
        Check if already task running.
        """
        user_account_qs = request.user.useraccount_set.filter(id=int(user_account_id))
        if user_account_qs.exists():
            user_account = user_account_qs.first()
            follow_jobs = user_account.job_set.filter(
                job_type="MULTI_USER_FOLLOW", status__in=["P", "I"]
            )
            job_usernames = []
            for job in follow_jobs:
                target_usernames = job.data.get("target_username", "")
                job_usernames += target_usernames.split(",")

            for user in job_usernames:
                if user in target_user:
                    target_user.remove(user)
                    removed_users.append(user)
        else:
            messages.error(request, "Please select an instagram account.")
            return render(request, self.template_name, self.get_context_data())
        """
        validate no. of follow
        """
        if group:
            group_accounts = UserAccount.objects.filter(group=group)
        else:
            group_accounts = None
        if group_accounts:
            for account in group_accounts:
                if int(number_of_followers) > 20:
                    messages.error(request, "Please enter less or equal 20 follows.")
                    return render(request, self.template_name, self.get_context_data())

                if len(target_user):
                    scheduled_for = parse(schedule_time)
                    scheduled_for = tz.make_aware(
                        scheduled_for, pytz.timezone(timezone)
                    )
                    Job.objects.create(
                        user=request.user,
                        user_account=account,
                        job_type="MULTI_USER_FOLLOW",
                        job_title="Follow Multiple Users",
                        app_type="IG",
                        scheduled_for=scheduled_for,
                        timezone=timezone,
                        status="P",
                        data={
                            "target_username": ",".join(target_user),
                            "times": number_of_followers,
                        },
                        like_comment=lik_cmnt_opt,
                        other_acc_not_followed_back=not_followed_back,
                        other_acc_followed_back=followed_back,
                    )
                    messages.success(request, "Multi Follow Job created!")

                if len(removed_users):
                    removed = ",".join(removed_users)
                    messages.error(
                        request,
                        f"Job pending for provided usernames please wait or Provide other then these usernames: {removed}",
                    )

            return render(request, self.template_name, self.get_context_data())

        else:
            if int(number_of_followers) > 20:
                messages.error(request, "Please enter less or equal 20 follows.")
                return render(request, self.template_name, self.get_context_data())

            if len(target_user):
                scheduled_for = parse(schedule_time)
                scheduled_for = tz.make_aware(scheduled_for, pytz.timezone(timezone))
                Job.objects.create(
                    user=request.user,
                    user_account=user_account,
                    job_type="MULTI_USER_FOLLOW",
                    job_title="Follow Multiple Users",
                    app_type="IG",
                    scheduled_for=scheduled_for,
                    timezone=timezone,
                    status="P",
                    data={
                        "target_username": ",".join(target_user),
                        "times": number_of_followers,
                    },
                    like_comment=lik_cmnt_opt,
                    other_acc_not_followed_back=not_followed_back,
                    other_acc_followed_back=followed_back,
                )
                messages.success(request, "Multi Follow Job created!")

            if len(removed_users):
                removed = ",".join(removed_users)
                messages.error(
                    request,
                    f"Job pending for provided usernames please wait or Provide other then these usernames: {removed}",
                )

            return render(request, self.template_name, self.get_context_data())


"""-----------------------------VIRAL IGNITOR TEMPLATES--------------------------------------------------"""


class TelegramDashboardIndexView(TemplateView):
    template_name = "dashboard/viral_ignitor/telegram_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        translation.activate(self.request.user.user_language)
        current = datetime.datetime.now()
        end = current - datetime.timedelta(days=29)
        dates = [(end + datetime.timedelta(days=x)).date() for x in range(0, 30)]
        (
            total_failed_jobs_count,
            total_pending_jobs_count,
            total_completed_jobs_count,
            total_count,
        ) = (0, 0, 0, 0)
        (
            date_list,
            failed_jobs_count_list,
            pending_jobs_count_list,
            completed_jobs_count_list,
        ) = ([], [], [], [])
        jobs_filters = [
            "LIKE_MULTIPLE_POSTS",
            "MULTI_USER_FOLLOW",
            "FOLLOW_TAGS",
            "AUTO_UNFOLLOW",
            "USERNAME_FOLLOW",
            "POST_STORY",
            "POST",
            "POST_VIDEO",
        ]
        jobs = self.request.user.job_set.filter(job_type__in=jobs_filters)
        try:
            for date in list(dates):
                failed_jobs_count = jobs.filter(status="F", created__date=date).count()
                pending_jobs_count = jobs.filter(status="P", created__date=date).count()
                completed_jobs_count = jobs.filter(
                    status="C", created__date=date
                ).count()
                date_list.append(str(date.strftime("%Y-%m-%d")))
                total_completed_jobs_count += completed_jobs_count
                total_pending_jobs_count += pending_jobs_count
                total_failed_jobs_count += failed_jobs_count
                failed_jobs_count_list.append(failed_jobs_count)
                pending_jobs_count_list.append(pending_jobs_count)
                completed_jobs_count_list.append(completed_jobs_count)
        except Exception as e:
            print(str(e))
        total_count = (
            total_completed_jobs_count
            + total_pending_jobs_count
            + total_failed_jobs_count
        )

        context["date"] = date_list
        context["failedJobsCount"] = failed_jobs_count_list
        context["pendingJobsCount"] = pending_jobs_count_list
        context["completedJobsCount"] = completed_jobs_count_list
        context["totalcompletedJobsCount"] = total_completed_jobs_count
        context["totalpendingJobsCount"] = total_pending_jobs_count
        context["totalfailedJobsCount"] = total_failed_jobs_count
        context["total_count"] = total_count
        return context

    def post(self, request, **kwargs):
        context = {}
        user_account_id = self.request.POST["insta_user_id"]
        user_account = UserAccount.objects.get(id=user_account_id)
        current = datetime.datetime.now()
        end = current - datetime.timedelta(days=29)
        dates = [(end + datetime.timedelta(days=x)).date() for x in range(0, 30)]
        (
            total_failed_jobs_count,
            total_pending_jobs_count,
            total_completed_jobs_count,
            total_count,
        ) = (0, 0, 0, 0)
        (
            date_list,
            failed_jobs_count_list,
            pending_jobs_count_list,
            completed_jobs_count_list,
        ) = ([], [], [], [])
        jobs_filters = [
            "LIKE_MULTIPLE_POSTS",
            "MULTI_USER_FOLLOW",
            "FOLLOW_TAGS",
            "AUTO_UNFOLLOW",
            "USERNAME_FOLLOW",
        ]
        jobs = Job.objects.filter(user_account=user_account).filter(
            job_type__in=jobs_filters
        )
        try:
            for date in list(dates):
                failed_jobs_count = jobs.filter(status="F", created__date=date).count()
                pending_jobs_count = jobs.filter(status="P", created__date=date).count()
                completed_jobs_count = jobs.filter(
                    status="C", created__date=date
                ).count()
                date_list.append(str(date.strftime("%Y-%m-%d")))
                total_completed_jobs_count += completed_jobs_count
                total_pending_jobs_count += pending_jobs_count
                total_failed_jobs_count += failed_jobs_count
                failed_jobs_count_list.append(failed_jobs_count)
                pending_jobs_count_list.append(pending_jobs_count)
                completed_jobs_count_list.append(completed_jobs_count)
        except Exception as e:
            print(str(e))

        total_count = (
            total_completed_jobs_count
            + total_pending_jobs_count
            + total_failed_jobs_count
        )

        context["date"] = date_list
        context["failedJobsCount"] = failed_jobs_count_list
        context["pendingJobsCount"] = pending_jobs_count_list
        context["completedJobsCount"] = completed_jobs_count_list
        context["totalcompletedJobsCount"] = total_completed_jobs_count
        context["totalpendingJobsCount"] = total_pending_jobs_count
        context["totalfailedJobsCount"] = total_failed_jobs_count
        context["total_count"] = total_count
        return render(request, self.template_name, context)


class DashboardIndexView(TemplateView):
    template_name = "dashboard/viral_ignitor/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        translation.activate(self.request.user.user_language)
        current = datetime.datetime.now()
        end = current - datetime.timedelta(days=29)
        dates = [(end + datetime.timedelta(days=x)).date() for x in range(0, 30)]
        (
            total_failed_jobs_count,
            total_pending_jobs_count,
            total_completed_jobs_count,
            total_count,
        ) = (0, 0, 0, 0)
        (
            date_list,
            failed_jobs_count_list,
            pending_jobs_count_list,
            completed_jobs_count_list,
        ) = ([], [], [], [])
        jobs_filters = [
            "LIKE_MULTIPLE_POSTS",
            "MULTI_USER_FOLLOW",
            "FOLLOW_TAGS",
            "AUTO_UNFOLLOW",
            "USERNAME_FOLLOW",
            "POST_STORY",
            "POST",
            "POST_VIDEO",
        ]
        jobs = self.request.user.job_set.filter(job_type__in=jobs_filters)
        try:
            for date in list(dates):
                failed_jobs_count = jobs.filter(status="F", created__date=date).count()
                pending_jobs_count = jobs.filter(status="P", created__date=date).count()
                completed_jobs_count = jobs.filter(
                    status="C", created__date=date
                ).count()
                date_list.append(str(date.strftime("%Y-%m-%d")))
                total_completed_jobs_count += completed_jobs_count
                total_pending_jobs_count += pending_jobs_count
                total_failed_jobs_count += failed_jobs_count
                failed_jobs_count_list.append(failed_jobs_count)
                pending_jobs_count_list.append(pending_jobs_count)
                completed_jobs_count_list.append(completed_jobs_count)
        except Exception as e:
            print(str(e))
        total_count = (
            total_completed_jobs_count
            + total_pending_jobs_count
            + total_failed_jobs_count
        )

        context["date"] = date_list
        context["failedJobsCount"] = failed_jobs_count_list
        context["pendingJobsCount"] = pending_jobs_count_list
        context["completedJobsCount"] = completed_jobs_count_list
        context["totalcompletedJobsCount"] = total_completed_jobs_count
        context["totalpendingJobsCount"] = total_pending_jobs_count
        context["totalfailedJobsCount"] = total_failed_jobs_count
        context["total_count"] = total_count
        return context

    def post(self, request, **kwargs):
        context = {}
        user_account_id = self.request.POST["insta_user_id"]
        user_account = UserAccount.objects.get(id=user_account_id)
        current = datetime.datetime.now()
        end = current - datetime.timedelta(days=29)
        dates = [(end + datetime.timedelta(days=x)).date() for x in range(0, 30)]
        (
            total_failed_jobs_count,
            total_pending_jobs_count,
            total_completed_jobs_count,
            total_count,
        ) = (0, 0, 0, 0)
        (
            date_list,
            failed_jobs_count_list,
            pending_jobs_count_list,
            completed_jobs_count_list,
        ) = ([], [], [], [])
        jobs_filters = [
            "LIKE_MULTIPLE_POSTS",
            "MULTI_USER_FOLLOW",
            "FOLLOW_TAGS",
            "AUTO_UNFOLLOW",
            "USERNAME_FOLLOW",
        ]
        jobs = Job.objects.filter(user_account=user_account).filter(
            job_type__in=jobs_filters
        )
        try:
            for date in list(dates):
                failed_jobs_count = jobs.filter(status="F", created__date=date).count()
                pending_jobs_count = jobs.filter(status="P", created__date=date).count()
                completed_jobs_count = jobs.filter(
                    status="C", created__date=date
                ).count()
                date_list.append(str(date.strftime("%Y-%m-%d")))
                total_completed_jobs_count += completed_jobs_count
                total_pending_jobs_count += pending_jobs_count
                total_failed_jobs_count += failed_jobs_count
                failed_jobs_count_list.append(failed_jobs_count)
                pending_jobs_count_list.append(pending_jobs_count)
                completed_jobs_count_list.append(completed_jobs_count)
        except Exception as e:
            print(str(e))

        total_count = (
            total_completed_jobs_count
            + total_pending_jobs_count
            + total_failed_jobs_count
        )

        context["date"] = date_list
        context["failedJobsCount"] = failed_jobs_count_list
        context["pendingJobsCount"] = pending_jobs_count_list
        context["completedJobsCount"] = completed_jobs_count_list
        context["totalcompletedJobsCount"] = total_completed_jobs_count
        context["totalpendingJobsCount"] = total_pending_jobs_count
        context["totalfailedJobsCount"] = total_failed_jobs_count
        context["total_count"] = total_count
        return render(request, self.template_name, context)


class DashboardInstagramView(TemplateView):
    template_name = "dashboard/viral_ignitor/instagram.html"


class PostView(TemplateView):
    template_name = "dashboard/viral_ignitor/post.html"

    def move_file_to_s3(self, file, file_path, bucket_name=None):
        if not bucket_name:
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        bucket_resource = s3
        resp = bucket_resource.upload_file(
            Bucket=bucket_name,
            Filename=file,
            Key=file_path,
            ExtraArgs={"ACL": "public-read"},
        )
        return resp

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_groups = SurviralGroup.objects.filter(user=user)
        context["user_groups"] = user_groups
        return context

    def post(self, request, **kwargs):
        insta_acc_id = self.request.POST["insta_user_id"]
        caption = self.request.POST["caption"]
        comment = self.request.POST.get("comment")
        scheduled_time = self.request.POST["time_post"]
        files = {"image": self.request.FILES["post-img"]}
        save_draft = self.request.POST.get("save_draft", False)
        group = self.request.POST.get("group", None)
        user = self.request.user

        temp_file = files["image"].name
        with open(temp_file, "wb+") as f:
            for chunk in files["image"].chunks():
                f.write(chunk)
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        file_path = "/surviral_web/post_image/" + files["image"].name
        temp_file_path = os.path.join(os.getcwd(), files["image"].name)
        self.move_file_to_s3(
            file=temp_file_path, file_path=file_path, bucket_name=bucket_name
        )
        if int(save_draft) == 1:
            save_draft = True
        if group:
            group_accounts = UserAccount.objects.filter(group=group)
        else:
            group_accounts = None
        scheduled_for = parse(scheduled_time)
        scheduled_for = tz.make_aware(
            scheduled_for, pytz.timezone(self.request.user.timezone)
        )
        caption = caption.replace('"', "").replace("'", "")
        comment = comment.replace('"', "").replace("'", "")
        if group_accounts:
            for account in group_accounts:
                try:
                    image_name = files["image"].name
                    Job.objects.create(
                        user=user,
                        user_account=account,
                        job_type="POST",
                        job_title="Post Job",
                        app_type="IG",
                        image=None,
                        scheduled_for=scheduled_for,
                        timezone=user.timezone,
                        status="P",
                        is_draft=save_draft,
                        data={
                            "caption": caption,
                            "comment": comment,
                            "file_name": image_name,
                            "file_path": file_path,
                        },
                    )

                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                    messages.success(request, "Post Job Created!")
                except Exception as e:
                    print(e)
                    messages.error(request, "There was an error while creating job.")
        else:
            try:
                image_name = files["image"].name
                account = UserAccount.objects.get(id=insta_acc_id)
                Job.objects.create(
                    user=user,
                    user_account=account,
                    job_type="POST",
                    job_title="Post Job",
                    app_type="IG",
                    image=None,
                    scheduled_for=scheduled_for,
                    timezone=user.timezone,
                    status="P",
                    is_draft=save_draft,
                    data={
                        "caption": caption,
                        "comment": comment,
                        "file_name": image_name,
                        "file_path": file_path,
                    },
                )
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                messages.success(request, "Post Job Created!")
            except Exception as e:
                print(e)
                messages.error(request, "There was an error while creating job.")
        return render(request, self.template_name, self.get_context_data())


class PostVideoView(TemplateView):
    template_name = "dashboard/viral_ignitor/post_video.html"

    def post(self, request, **kwargs):
        insta_acc_id = self.request.POST["insta_user_id"]
        caption = self.request.POST["caption"]
        comment = self.request.POST["caption"]
        scheduled_time = self.request.POST["time_post"]
        files = self.request.FILES["post-vid"]
        file_name = files["post-vid"].name
        file_path = files["post-vid"].name
        user = self.request.user
        scheduled_time = parse(scheduled_time)
        scheduled_for = tz.make_aware(scheduled_time, pytz.timezone(user.timezone))
        try:
            instagram_account = UserAccount.objects.get(id=insta_acc_id)
            job = Job.objects.create(
                user=user,
                user_account=instagram_account,
                job_type="POST",
                job_title="Post Job",
                app_type="IG",
                image=None,
                scheduled_for=scheduled_for,
                timezone=user.timezone,
                status="P",
                data={
                    "caption": caption,
                    "comment": comment,
                    "file_name": file_name,
                    "file_path": file_path,
                },
            )

            messages.success(request, "Post Job Created!")
        except Exception as e:
            print(e)
            messages.error(request, "There was an error while creating job.")

        return render(request, self.template_name, {})


class PostStoryView(TemplateView):
    template_name = "dashboard/viral_ignitor/create_story.html"

    def move_file_to_s3(self, file, file_path, bucket_name=None):
        if not bucket_name:
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        bucket_resource = s3
        resp = bucket_resource.upload_file(
            Bucket=bucket_name,
            Filename=file,
            Key=file_path,
            ExtraArgs={"ACL": "public-read"},
        )
        return resp

    def post(self, request, **kwargs):
        insta_acc_id = self.request.POST["insta_user_id"]
        caption = self.request.POST.get("caption", "")
        scheduled_time = self.request.POST["time_post"]
        user_id = self.request.POST["user"]
        # files = {'image': self.request.FILES['post-stry']}
        save_draft = request.POST.get("save_draft", False)
        # url = URL + 'image_post/'
        if int(save_draft) == 1:
            save_draft = True

        files = self.request.FILES
        multi_dict = files.getlist("post-stry")
        files_name = {}
        files_path = {}
        for file, i in zip(multi_dict, range(len(multi_dict))):
            temp_file = file.name
            files_name.update({f"image_{i}": file.name})
            with open(temp_file, "wb+") as f:
                for chunk in file.chunks():
                    f.write(chunk)
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            file_path = "/surviral_web/post_image/" + file.name
            files_path.update({f"file_path_{i}": file_path})
            temp_file_path = os.path.join(os.getcwd(), file.name)
            self.move_file_to_s3(
                file=temp_file_path, file_path=file_path, bucket_name=bucket_name
            )

        timezone = self.request.POST.get("timezone")
        scheduled_for = parse(scheduled_time)
        scheduled_for = tz.make_aware(scheduled_for, pytz.timezone(timezone))
        try:
            data = {
                "user": int(user_id),
                "insta_acc_id": int(insta_acc_id),
                "caption": caption,
                "scheduled_time": scheduled_time,
                "file_name": files_name,
                "file_path": files_path,
            }
            username = User.objects.get(pk=user_id)
            user_account = UserAccount.objects.filter(id=insta_acc_id).first()
            job = Job.objects.create(
                user=username,
                job_type="POST_STORY",
                job_title="Post multiple story",
                user_account=user_account,
                app_type="IG",
                status="P",
                is_draft=save_draft,
                timezone=timezone,
                scheduled_for=scheduled_for,
                data=data,
            )

            # Get device of the user account
            try:
                device = Device.objects.filter(accounts=user_account).first()

                if not device:
                    all_devices = Device.objects.all()
                    if len(all_devices) > 0:
                        device = random.choice(all_devices)
                        device.accounts.add(user_account)
                        device.save()

                JobQueue.objects.create(job=job, status="P", device=device)
            except Exception as e:
                print(e)
                messages.error(request, "There was an error while creating job.")
                return render(request, self.template_name, self.get_context_data())

            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

            messages.success(request, "Post Job Created!")
        except Exception as e:
            print(e)
            messages.error(request, "There was an error while creating job.")

        return render(request, self.template_name, {})


class InstagramPostView(TemplateView):
    template_name = "dashboard/viral_ignitor/instagram_post.html"


class InstagramActivityView(TemplateView):
    template_name = "dashboard/viral_ignitor/instagram_activity.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        insta_user_id = self.kwargs.get("insta_user_id", None)
        insta_account = self.request.user.useraccount_set.get(id=insta_user_id)
        context["jobs"] = job_qs = insta_account.job_set.filter(status="C")
        context["insta_account"] = insta_account

        total_likes = 0
        total_follows = 0
        total_unfollows = 0
        total_post_image_jobs = 0
        total_hashtag_likes = 0
        total_hashtag_follows = 0

        like_jobs = job_qs.filter(job_type="LIKE_MULTIPLE_POSTS")
        follow_jobs = job_qs.filter(job_type="MULTI_USER_FOLLOW")
        single_follow_jobs = job_qs.filter(job_type="USERNAME_FOLLOW")
        unfollow_jobs = job_qs.filter(job_type="AUTO_UNFOLLOW")
        post_image_jobs = job_qs.filter(job_type__in=["POST", "MULTI_IMAGE_POST"])
        hashtag_like_jobs = job_qs.filter(job_type="LIKE_MULTIPLE_POSTS")
        hashtag_follow_jobs = job_qs.filter(job_type="FOLLOW_TAGS")

        for like_job in like_jobs:
            total_likes += int(like_job.data["num_of_likes"])

        for follow_job in follow_jobs:
            total_follows += int(follow_job.data["times"])

        for single_follow in single_follow_jobs:
            total_follows += len(single_follow.data.get("target_user", "").split(","))

        for unfollow_job in unfollow_jobs:
            total_unfollows += int(unfollow_job.data["times"])

        for hashtag_follow_job in hashtag_follow_jobs:
            total_hashtag_follows += int(
                hashtag_follow_job.data["num_of_accounts_to_follow"]
            )

        for hashtag_like_job in hashtag_like_jobs:
            total_hashtag_likes += int(hashtag_like_job.data["num_of_likes"])

        for post in post_image_jobs:
            total_post_image_jobs += 1

        context["likes"] = total_likes
        context["follows"] = total_follows
        context["unfollows"] = total_unfollows
        context["total_post_image_jobs"] = total_post_image_jobs
        context["total_hashtag_likes"] = total_hashtag_likes
        context["total_hashtag_follows"] = total_hashtag_follows
        return context


class InstagramAnalyticsView(TemplateView):
    template_name = "dashboard/viral_ignitor/instagram_analytics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        insta_user_id = self.kwargs.get("insta_user_id", None)
        insta_user_id = (
            insta_user_id
            if insta_user_id
            else self.request.user.useraccount_set.first().id
        )
        context["mt_user_accounts"] = UserAccount.objects.filter(
            account_from__in=["MT", "M"]
        )
        if insta_user_id:
            insta_account = UserAccount.objects.get(id=insta_user_id)
            query_set = (
                DailyAccountData.objects.filter(user_account=insta_account)
                .distinct("created__date")
                .order_by("-created__date")
            )
            created = list(query_set.values_list("created", flat=True))
            followers = ["Follower"] + list(
                query_set.values_list("followers", flat=True)
            )
            following = ["Following"] + list(
                query_set.values_list("following", flat=True)
            )
            cta = ["cta"] + list(query_set.values_list("cta", flat=True))
            today_followers = ["New Followers"] + list(
                query_set.values_list("today_followers", flat=True)
            )
            follow_bk_per = ["Follow Back %"] + list(
                query_set.values_list("follow_bk_per", flat=True)
            )
            new_dm = ["New DM"] + [0 for x in created]
            feed_post = ["Feed Post"] + [0 for x in created]
            story_post = ["Story Post"] + [0 for x in created]
            comment_follow = ["Comment Follow"] + list(
                query_set.values_list("comment_follow", flat=True)
            )
            follow = ["Follow"] + list(
                query_set.values_list("comment_follow", flat=True)
            )
            unfollow = ["Unfollow"] + list(query_set.values_list("unfollow", flat=True))
            story_dm = ["Story DM"] + [0 for x in created]
            thank_u_dm = ["Thank you DM"] + list(
                query_set.values_list("thank_u_dm", flat=True)
            )
            comment_post = ["Comment Post"] + list(
                query_set.values_list("comment_post", flat=True)
            )
            context["account_analytics"] = [
                created,
                followers,
                following,
                cta,
                today_followers,
                follow_bk_per,
                new_dm,
                feed_post,
                story_post,
                comment_follow,
                follow,
                unfollow,
                story_dm,
                thank_u_dm,
                comment_post,
            ]
            # context['account_analytics'] = user_account.account_analytic.distinct("created").all().order_by("-created")
            context["user_account"] = insta_account
        return context


class AccountManagerView(TemplateView):
    template_name = "dashboard/viral_ignitor/account_manager.html"


class FileManagerView(TemplateView):
    template_name = "dashboard/viral_ignitor/file_manager.html"


class GroupManagerView(TemplateView):
    template_name = "dashboard/viral_ignitor/group_manager.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["groups"] = self.request.user.surviralgroup_set.all()
        context["insta_accounts"] = self.request.user.useraccount_set.filter(
            group__in=context["groups"], login_status="IN"
        )
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        account = request.user.useraccount_set.filter(id=self.kwargs.get("insta_id"))
        if account.exists():
            rm_group = UserAccount.objects.get(id=self.kwargs.get("insta_id"))
            rm_group.group = None
            rm_group.save()
            messages.success(request, "Instagram Account Remove successfully!")
            return redirect("group_manager")
        return render(request, self.template_name, context)


class CaptionView(TemplateView):
    template_name = "dashboard/viral_ignitor/caption.html"


class WaterMarkView(TemplateView):
    template_name = "dashboard/viral_ignitor/watermark.html"


class PricingView(TemplateView):
    template_name = "dashboard/viral_ignitor/pricing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plans = Plan.objects.filter(is_active=True, plan_type="month")
        yearly_plans = Plan.objects.filter(is_active=True, plan_type="year")

        context["plans"] = plans
        context["yearly_plans"] = yearly_plans
        return context


class SettingsView(TemplateView):
    template_name = "dashboard/viral_ignitor/settings.html"


class ProfileView(TemplateView):
    template_name = "dashboard/viral_ignitor/profile.html"


class StatsView(TemplateView):
    template_name = "dashboard/viral_ignitor/stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        insta_user_id = self.kwargs.get("insta_user_id")
        insta_account = self.request.user.useraccount_set.get(id=insta_user_id)
        now = datetime.datetime.now()
        # days = [now - datetime.timedelta(days=x) for x in range(7)]

        end = now - datetime.timedelta(days=6)
        days = [(end + datetime.timedelta(days=x)) for x in range(0, 7)]
        context["insta_account"] = insta_account
        context["days"] = []
        context["single_follow"] = []
        context["multiple_follow"] = []
        context["multiple_unfollow"] = []
        context["hashtag_follow"] = []
        context["hashtag_like"] = []
        for day in days:
            context["days"].append(day.strftime("%Y-%m-%d"))
            job_stats = Job.objects.filter(
                created__date=day.date(), user_account=insta_account, app_type="IG"
            )
            context["single_follow"].append(
                job_stats.filter(job_type="USERNAME_FOLLOW").count()
            )
            context["multiple_follow"].append(
                job_stats.filter(job_type="MULTI_USER_FOLLOW").count()
            )
            context["multiple_unfollow"].append(
                job_stats.filter(job_type="AUTO_UNFOLLOW").count()
            )
            context["hashtag_follow"].append(
                job_stats.filter(job_type="FOLLOW_TAGS").count()
            )
            context["hashtag_like"].append(
                job_stats.filter(job_type="LIKE_MULTIPLE_POSTS").count()
            )
        return context


class LogView(TemplateView):
    template_name = "dashboard/viral_ignitor/log.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        insta_user_id = self.kwargs.get("insta_user_id")
        option = self.kwargs.get("option")
        insta_account = self.request.user.useraccount_set.get(id=insta_user_id)
        context["insta_account"] = insta_account
        context["data"] = Job.objects.filter(
            user_account=insta_account, app_type="IG"
        ).order_by("-created")
        if option:
            context["data"] = Job.objects.filter(
                user_account=insta_account, app_type="IG", job_type=option
            ).order_by("-created")
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        """
        Delete Job
        """
        user_account_id = self.kwargs.get("insta_user_id")
        job_id = self.kwargs.get("delete_job_id")
        user = request.user
        if job_id:
            job_qs = user.job_set.filter(id=job_id, status="P")
            if job_qs.exists():
                job_qs.delete()
                messages.success(request, "Job deleted successfully.")
            else:
                messages.error(request, "Unable to delete job.")
            return redirect("log", user_account_id)
        return render(request, self.template_name, context)


class PaymentView(TemplateView):
    template_name = "dashboard/viral_ignitor/payment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stripe_plan_id = self.kwargs.get("plan_id")
        plans = Plan.objects.filter(stripe_plan_id=stripe_plan_id)
        if plans:
            context["plan"] = plans.first()
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        name = request.POST["name"]
        line1 = request.POST["line1"]
        country = request.POST["country"]
        if not hasattr(request.user, "stripe_user"):
            utils.create_stripe_customer(request.user, line1, country)
        stripe_user = request.user.stripe_user

        card_id = request.POST.get("card_id", None)
        try:
            stripe_customer_card = None
            if card_id == "other_card":
                card_number = request.POST["card_number"]
                expiry = request.POST["expiry"]
                expiry_month = int(expiry.split("/")[0])
                expiry_year = int(expiry.split("/")[1])
                cvv = request.POST["cvv"]

                source = utils.create_card_token(
                    card_number, expiry_month, expiry_year, cvv
                )
                stripe_customer_card = utils.assign_source_to_customer(
                    stripe_user, source
                )
            else:
                stripe_customer_card = card_id
            subscription_id = utils.subscribe_stripe_user(
                context["plan"], stripe_user, request.user
            )
            utils.save_payment_history(
                request.user, context["plan"].amount, subscription_id
            )
            context["subscription_id"] = subscription_id

        except Exception as ex:

            context["message"] = ex.json_body["error"]["message"]

            context["card_number"] = card_number
            context["expiry"] = expiry
            context["cvv"] = cvv
            if stripe_customer_card:
                utils.remove_customer_cards(
                    stripe_user.stripe_customer_id, stripe_customer_card
                )
            context["name"] = name
            context["line1"] = line1
            context["country"] = country
        return render(request, self.template_name, context)


class DeleteAccountQuickView(TemplateView):
    template_name = "dashboard/viral_ignitor/multistep-form.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        account = request.user.useraccount_set.filter(
            id=self.kwargs.get("delete_account")
        )
        if account.exists():
            account.delete()
            messages.success(request, "Instagram Account Deleted successfully!")
            return redirect("multistep_form")
        elif self.kwargs.get("delete_account"):
            messages.error(request, "Instagram Account Not Found.")
        return render(request, self.template_name, context)


class InstagramAccountView(TemplateView):
    template_name = "dashboard/viral_ignitor/add_instagram_account.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["countries"] = constants.COUNTRIES
        context["groups"] = self.request.user.surviralgroup_set.all()
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        # context['verified'] = 'Yes' if request.user.email_verified else 'No'
        account = request.user.useraccount_set.filter(
            id=self.kwargs.get("delete_account")
        )
        if account.exists():
            account.delete()
            messages.success(request, "Instagram Account Deleted successfully!")
            return redirect("account_manager")
        elif self.kwargs.get("delete_account"):
            messages.error(request, "Instagram Account Not Found.")
        return render(request, self.template_name, context)

    def post(self, request):
        context = self.get_context_data()
        form = AddInstagramAccountForm(data=self.request.POST)
        if request.user.useraccount_set.filter(account_from="CL").count() >= 100:
            msg = "You have exceeded max add instagram account limit."
            messages.error(request, f"{msg}")
            return render(request, self.template_name, context)

        if form.is_valid():
            account_username = self.request.POST.get("account_username")
            account_password = self.request.POST.get("account_password")
            otp_mode = self.request.POST.get("otp_mode")
            country_code = self.request.POST.get("area_country")
            group_name = self.request.POST.get("area_group")
            twofa_check = self.request.POST.get("2fa_codes_check", False)
            twofa_codes = self.request.POST.get("2fa_codes")
            user = self.request.user
            otp_mode = 0 if otp_mode == "Phone" else 1

            if twofa_check:
                twofa_check = True

            if SurviralGroup.objects.filter(id=int(group_name)).exists():
                group = SurviralGroup.objects.get(id=int(group_name))
            else:
                group = None

            user_account = UserAccount.objects.create(
                user=user,
                account_type="IG",
                auth_type="CL",
                account_username=account_username,
                account_password=account_password,
                account_for="W",
                country=country_code,
                data={"otp_mode": otp_mode},
                group=group,
                status="A",
                twofa_codes=twofa_codes,
                twofa_protected=twofa_check,
            )
            Job.objects.create(
                user=user_account.user,
                user_account=user_account,
                job_type="GET_PROFILE",
                job_title="""Get User's Profile""",
                app_type="IG",
                scheduled_for=datetime.datetime.now(pytz.utc),
                status="P",
            )

            try:
                device = Device.objects.filter(accounts=user_account).first()

                if not device:
                    all_devices = Device.objects.all()
                    device = random.choice(all_devices)
                    device.accounts.add(user_account)
                    device.save()

            except Exception as e:
                print(e)

            messages.success(request, f"Account added successfully.")
            return redirect("account_manager")
        for key, error in enumerate(form.errors):
            msg = form.errors[error]
            messages.error(request, f"{msg}")
        context["form"] = form
        return render(request, self.template_name, context)


class InsertOTPView(CreateView):
    def post(self, request, *args, **kwargs):
        user_account = UserAccount.objects.get(id=self.request.POST.get("user_id"))
        if "otp" in self.request.POST:
            otp = self.request.POST.get("otp")
            user_account.data["otp"] = otp
            user_account.login_status = "P"
            user_account.save()
            messages.success(request, "Got OTP!")
        else:
            messages.error(request, constants.OTP_REQUIRED_MESSAGE)
        return redirect("account_manager")


class SchedulesView(TemplateView):
    template_name = "dashboard/viral_ignitor/schedules.html"


class InstaAccountGeneralDetails(TemplateView):
    template_name = "dashboard/viral_ignitor/multistep-form.html"

    def post(self, request, *args, **kwargs):
        insta_account = self.request.POST.get("insta_account")
        insta_passwd = self.request.POST.get("insta_password")
        account_data = self.request.POST.get("insta_account_about")
        print("details ", insta_account, insta_passwd, account_data)

        if insta_account and insta_passwd and account_data:
            created = UserAccount.objects.create(
                user=self.request.user,
                account_type="IG",
                account_username=insta_account,
                account_password=insta_passwd,
                status="A",
                data={"account_data": account_data},
            )
            print(created, " created")
        return redirect("multistep_form")


class InstaAccountActionDetailsView(TemplateView):
    template_name = "dashboard/viral_ignitor/multistep-form.html"

    def post(self, request, *args, **kwargs):
        target_audience = self.request.POST.get("target_audience")
        target_area = self.request.POST.get("target_area")
        target_gender = self.request.POST.get("target_gender")
        yourCompetitors = self.request.POST.get("yourCompetitors")
        insta_account_id = self.request.POST.get("insta_account_id")

        if target_audience and target_area and target_gender and yourCompetitors:
            UserAccount.objects.filter(id=insta_account_id).update(
                target_auidience=target_audience,
                competitors=yourCompetitors,
                target_area=target_area,
                target_gender=target_gender,
            )
        return redirect("multistep_form")


class CreateInstagramBot(TemplateView):
    template_name = "dashboard/tools/create_bot.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["phone_countries"] = constants.SMS_COUNTRIES
        context["countries"] = constants.COUNTRIES
        return context

    def post(self, request):
        context = self.get_context_data()
        data = self.request.POST
        full_name = data.get("full_name")
        username = data.get("username")
        password = data.get("password")
        timezone = data.get("timezone")
        usernames, max_tries, bots_number = [], 0, 1
        user_account_qs = UserAccount.objects.filter(
            account_from="CO", created__date=datetime.datetime.now().date()
        )

        banned_country = list(
            set(
                user_account_qs.filter(login_status="OUT").values_list(
                    "country", flat=True
                )
            )
        )
        last_country = (
            user_account_qs.order_by("id").last().country
            if user_account_qs.exists()
            else None
        )

        if last_country not in banned_country:
            banned_country.append(last_country)

        """
        Filter Available Country
        """
        countries = [x for x in constants.VPN_COUNTRIES]
        for country in countries:
            if country in banned_country:
                countries.remove(country)
        if len(countries):
            random.shuffle(countries)
            selected_country = countries[0]
        else:
            countries = [x for x in constants.VPN_COUNTRIES]
            random.shuffle(countries)
            selected_country = countries[0]

        while len(usernames) < bots_number:
            if max_tries == 10:
                break
            day_random_prefix = str(random.randrange(1, 30)).zfill(2)
            month_random_prefix = str(random.randrange(1, 12)).zfill(2)
            changed_username = f"{username}_{day_random_prefix}{month_random_prefix}"
            account_exists = UserAccount.objects.filter(
                account_username=changed_username
            ).exists()

            if not account_exists:
                usernames.append(changed_username)
            else:
                max_tries += 1

        if not len(usernames) == bots_number:
            messages.error(
                request, "Username not available, Please provide a unique username."
            )
            return render(request, self.template_name, context)

        if full_name and username and password:
            for username in usernames:
                user_account = UserAccount.objects.create(
                    user=self.request.user,
                    account_type="IG",
                    account_from="CO",
                    full_name=full_name,
                    account_username=username,
                    account_password=password,
                    phone_country=selected_country,
                    country=selected_country,
                    status="A",
                    data={},
                )

                Job.objects.create(
                    user=user_account.user,
                    user_account=user_account,
                    job_type="CREATE_BOT",
                    job_title="""Create Instgram bot""",
                    app_type="IG",
                    timezone=timezone,
                    scheduled_for=datetime.datetime.now(pytz.utc),
                    status="P",
                )
            messages.success(
                request, "Bot Creation Tasks have been added successfully."
            )
        return render(request, self.template_name, context)


class PublishAllView(TemplateView):
    template_name = "dashboard/viral_ignitor/post.html"

    def move_file_to_s3(self, file, file_path, bucket_name=None):
        if not bucket_name:
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        bucket_resource = s3
        resp = bucket_resource.upload_file(
            Bucket=bucket_name,
            Filename=file,
            Key=file_path,
            ExtraArgs={"ACL": "public-read"},
        )
        return resp

    def post(self, request, **kwargs):
        insta_acc_id = self.request.POST["insta_user_id"]
        caption = self.request.POST["caption"]
        comment = self.request.POST.get("comment")
        scheduled_time = self.request.POST["time_post"]
        files = {"image": self.request.FILES["post-img"]}
        save_draft = self.request.POST.get("save_draft", False)
        group = self.request.POST.get("group", None)
        user = self.request.user

        temp_file = files["image"].name
        with open(temp_file, "wb+") as f:
            for chunk in files["image"].chunks():
                f.write(chunk)
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        file_path = "/surviral_web/post_image/" + files["image"].name
        temp_file_path = os.path.join(os.getcwd(), files["image"].name)
        self.move_file_to_s3(
            file=temp_file_path, file_path=file_path, bucket_name=bucket_name
        )

        if int(save_draft) == 1:
            save_draft = True
        if group:
            group_accounts = UserAccount.objects.filter(group=group)
        else:
            group_accounts = None
        scheduled_for = parse(scheduled_time)
        scheduled_for = tz.make_aware(
            scheduled_for, pytz.timezone(self.request.user.timezone)
        )
        caption = caption.replace('"', "").replace("'", "")
        comment = comment.replace('"', "").replace("'", "")
        if group_accounts:
            for account in group_accounts:
                try:
                    image_name = files["image"].name
                    Job.objects.create(
                        user=user,
                        user_account=account,
                        job_type="POST",
                        job_title="Post Job",
                        app_type="IG",
                        image=None,
                        scheduled_for=scheduled_for,
                        timezone=user.timezone,
                        status="P",
                        is_draft=save_draft,
                        data={
                            "caption": caption,
                            "comment": comment,
                            "file_name": image_name,
                            "file_path": file_path,
                        },
                    )

                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                    messages.success(request, "Post Job Created!")
                except Exception as e:
                    print(e)
                    messages.error(request, "There was an error while creating job.")
        else:
            try:
                image_name = files["image"].name
                account = UserAccount.objects.get(id=insta_acc_id)
                Job.objects.create(
                    user=user,
                    user_account=account,
                    job_type="POST",
                    job_title="Post Job",
                    app_type="IG",
                    image=None,
                    scheduled_for=scheduled_for,
                    timezone=user.timezone,
                    status="P",
                    is_draft=save_draft,
                    data={
                        "caption": caption,
                        "comment": comment,
                        "file_name": image_name,
                        "file_path": file_path,
                    },
                )
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                messages.success(request, "Post Job Created!")
            except Exception as e:
                print(e)
                messages.error(request, "There was an error while creating job.")
        return render(request, self.template_name, self.get_context_data())


class PostImageView(TemplateView):
    template_name = "dashboard/viral_ignitor/post.html"

    def move_file_to_s3(self, file, file_path, bucket_name=None):
        if not bucket_name:
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        bucket_resource = s3
        resp = bucket_resource.upload_file(
            Bucket=bucket_name,
            Filename=file,
            Key=file_path,
            ExtraArgs={"ACL": "public-read"},
        )
        return resp

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_groups = SurviralGroup.objects.filter(user=user)
        context["user_groups"] = user_groups
        return context

    def post(self, request, **kwargs):
        insta_acc_id = self.request.POST["insta_user_id"]
        caption = self.request.POST["caption"]
        comment = self.request.POST.get("comment")
        scheduled_time = self.request.POST["time_post"]
        files = {"image": self.request.FILES["post-img"]}
        save_draft = self.request.POST.get("save_draft", False)
        group = self.request.POST.get("group", None)
        user = self.request.user

        temp_file = files["image"].name
        with open(temp_file, "wb+") as f:
            for chunk in files["image"].chunks():
                f.write(chunk)
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        file_path = "/surviral_web/post_image/" + files["image"].name
        temp_file_path = os.path.join(os.getcwd(), files["image"].name)
        self.move_file_to_s3(
            file=temp_file_path, file_path=file_path, bucket_name=bucket_name
        )

        if int(save_draft) == 1:
            save_draft = True
        if group:
            group_accounts = UserAccount.objects.filter(group=group)
        else:
            group_accounts = None
        scheduled_for = parse(scheduled_time)
        scheduled_for = tz.make_aware(
            scheduled_for, pytz.timezone(self.request.user.timezone)
        )
        caption = caption.replace('"', "").replace("'", "")
        if comment:
            comment = comment.replace('"', "").replace("'", "")
        else:
            comment = ""
        if group_accounts:
            for account in group_accounts:
                try:
                    image_name = files["image"].name
                    Job.objects.create(
                        user=user,
                        user_account=account,
                        job_type="POST",
                        job_title="Post Job",
                        app_type="IG",
                        image=None,
                        scheduled_for=scheduled_for,
                        timezone=user.timezone,
                        status="P",
                        is_draft=save_draft,
                        data={
                            "caption": caption,
                            "comment": comment,
                            "file_name": image_name,
                            "file_path": file_path,
                        },
                    )

                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                    messages.success(request, "Post Job Created!")
                except Exception as e:
                    print(e)
                    messages.error(request, "There was an error while creating job.")
        else:
            try:
                image_name = files["image"].name
                account = UserAccount.objects.get(id=insta_acc_id)
                Job.objects.create(
                    user=user,
                    user_account=account,
                    job_type="POST",
                    job_title="Post Job",
                    app_type="IG",
                    image=None,
                    scheduled_for=scheduled_for,
                    timezone=user.timezone,
                    status="P",
                    is_draft=save_draft,
                    data={
                        "caption": caption,
                        "comment": comment,
                        "file_name": image_name,
                        "file_path": file_path,
                    },
                )
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                messages.success(request, "Post Job Created!")
            except Exception as e:
                print(e)
                messages.error(request, "There was an error while creating job.")
        return render(request, self.template_name, self.get_context_data())


class PostMultiImageView(TemplateView):
    template_name = "dashboard/viral_ignitor/photo_post.html"

    def move_file_to_s3(self, file, file_path, bucket_name=None):
        if not bucket_name:
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        bucket_resource = s3
        resp = bucket_resource.upload_file(
            Bucket=bucket_name,
            Filename=file,
            Key=file_path,
            ExtraArgs={"ACL": "public-read"},
        )
        return resp

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_groups = SurviralGroup.objects.filter(user=user)
        context["user_groups"] = user_groups
        return context

    def post(self, request, **kwargs):
        insta_acc_id = self.request.POST["insta_user_id"]
        caption = self.request.POST["caption"]
        scheduled_time = self.request.POST["time_post"]
        user_id = self.request.POST["user"]
        save_draft = self.request.POST.get("save_draft", False)
        group = self.request.POST.get("group", "")
        files = self.request.FILES
        multi_dict = files.getlist("post-img")
        files_name = {}
        files_path = {}
        for file, i in zip(multi_dict, range(len(multi_dict))):
            temp_file = file.name
            files_name.update({f"image_{i}": file.name})
            with open(temp_file, "wb+") as f:
                for chunk in file.chunks():
                    f.write(chunk)
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            file_path = "/surviral_web/post_image/" + file.name
            files_path.update({f"file_path_{i}": file_path})
            temp_file_path = os.path.join(os.getcwd(), file.name)
            self.move_file_to_s3(
                file=temp_file_path, file_path=file_path, bucket_name=bucket_name
            )

        # url = URL + 'image_post/'
        if int(save_draft) == 1:
            save_draft = True
        timezone = self.request.POST.get("timezone")
        scheduled_for = parse(scheduled_time)
        scheduled_for = tz.make_aware(
            scheduled_for, pytz.timezone(self.request.user.timezone)
        )
        try:
            data = {
                "user": int(user_id),
                "insta_acc_id": int(insta_acc_id),
                "caption": caption,
                "scheduled_time": scheduled_time,
                "file_name": files_name,
                "file_path": files_path,
            }
            username = User.objects.get(pk=user_id)
            if group:
                group_accounts = UserAccount.objects.filter(group=group)
            else:
                group_accounts = None
            if group_accounts:
                for account in group_accounts:
                    job = Job.objects.create(
                        user=username,
                        job_type="MULTI_IMAGE_POST",
                        job_title="Post multiple images",
                        user_account=account,
                        app_type="IG",
                        status="P",
                        is_draft=save_draft,
                        timezone=timezone,
                        scheduled_for=scheduled_for,
                        data=data,
                    )

                    # Get device of the user account
                    try:
                        device = Device.objects.filter(accounts=account).first()

                        if not device:
                            all_devices = Device.objects.all()
                            if len(all_devices) > 0:
                                device = random.choice(all_devices)
                                device.accounts.add(account)
                                device.save()

                        JobQueue.objects.create(job=job, status="P", device=device)
                    except Exception as e:
                        print(e)
                        messages.error(
                            request, "There was an error while creating job."
                        )
                        return render(
                            request, self.template_name, self.get_context_data()
                        )

                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            else:
                user_account = UserAccount.objects.filter(id=insta_acc_id).first()
                job = Job.objects.create(
                    user=username,
                    job_type="MULTI_IMAGE_POST",
                    job_title="Post multiple images",
                    user_account=user_account,
                    app_type="IG",
                    status="P",
                    is_draft=save_draft,
                    timezone=timezone,
                    scheduled_for=scheduled_for,
                    data=data,
                )

                # Get device of the user account
                try:
                    device = Device.objects.filter(accounts=user_account).first()

                    if not device:
                        all_devices = Device.objects.all()
                        if len(all_devices) > 0:
                            device = random.choice(all_devices)
                            device.accounts.add(user_account)
                            device.save()

                    JobQueue.objects.create(job=job, status="P", device=device)
                except Exception as e:
                    print(e)
                    messages.error(request, "There was an error while creating job.")
                    return render(request, self.template_name, self.get_context_data())

                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

            messages.success(request, "Post Job Created!")
        except Exception as e:
            print(e)
            messages.error(request, "There was an error while creating job.")

        return render(request, self.template_name, self.get_context_data())


class CreateGroup(TemplateView):
    template_name = "dashboard/viral_ignitor/create_group.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request):
        context = self.get_context_data()
        data = self.request.POST
        group_name = data.get("group_name")
        description = data.get("description")

        if group_name and description:
            user_group = SurviralGroup.objects.create(
                name=group_name, user=self.request.user, desc=description
            )
            messages.success(request, "Group have been added successfully.")
            return redirect("group_manager")
        return render(request, self.template_name, context)


class LinkToGroupView(TemplateView):
    template_name = "dashboard/viral_ignitor/updat_insta_accounts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["groups"] = self.request.user.surviralgroup_set.all()
        context["current_group"] = self.request.user.surviralgroup_set.first()
        context["list_insta"] = self.request.user.surviralgroup_set.filter(
            id=self.kwargs.get("group_id")
        ).first()
        context["account"] = self.request.user.useraccount_set.filter(
            group=context["list_insta"]
        )
        context["accounts"] = self.request.user.useraccount_set.filter(
            group__isnull=True
        )

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        data = self.request.POST
        group_id = data.get("insta_group_id")
        insta_ids = data.getlist("insta_account")
        user = request.user
        if not insta_ids:
            messages.error(request, "please select instagram accounts")
            return redirect("group_manager")
        try:
            user_account_qs = user.surviralgroup_set.filter(id=group_id).first()
        except:
            user_account_qs = None
        if user_account_qs:
            for insta_id in insta_ids:
                user_account = UserAccount.objects.get(user=user, id=insta_id)

                user_account.group = user_account_qs
                user_account.save()
            messages.success(request, "Group link successfully.")
            return redirect("group_manager")

        messages.error(request, "Group does not exists.")
        return redirect("group_manager")


class ListInstAccountView(TemplateView):
    template_name = "dashboard/viral_ignitor/group_manager.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["groups"] = self.request.user.surviralgroup_set.all()
        context["list_insta"] = self.request.user.surviralgroup_set.filter(
            id=self.kwargs.get("group_id")
        )
        context["insta_accounts"] = self.request.user.useraccount_set.filter(
            group__in=context["list_insta"], login_status="IN"
        )
        context["group_name"] = (
            self.request.user.surviralgroup_set.filter(id=self.kwargs.get("group_id"))
            .first()
            .name
        )
        return context


class DeleteGroupView(TemplateView):
    template_name = "dashboard/viral_ignitor/updat_insta_accounts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["groups"] = self.request.user.surviralgroup_set.all()
        context["current_group"] = self.request.user.surviralgroup_set.first()
        context["list_insta"] = self.request.user.surviralgroup_set.filter(
            id=self.kwargs.get("group_id")
        ).first()
        context["account"] = self.request.user.useraccount_set.filter(
            group=context["list_insta"]
        )
        context["accounts"] = self.request.user.useraccount_set.filter(
            group__isnull=True
        )

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        account = request.user.surviralgroup_set.filter(id=self.kwargs.get("group_id"))
        if account.exists():
            rm_group = SurviralGroup.objects.get(id=self.kwargs.get("group_id"))
            rm_group.delete()
            messages.success(request, "Instagram Group Delete successfully!")
            return redirect("group_manager")
        return render(request, self.template_name, context)


class LikeOnYoutubeVideoAPIView(TemplateView):
    template_name = "dashboard/tools/youtube_like.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_accounts = YoutubeAccount.objects.all()
        user_groups = YoutubeGroup.objects.all()
        context["user_accounts"] = user_accounts
        context["user_groups"] = user_groups
        return context

    def post(self, request, *args, **kwargs):
        
        
        
        
        # ----------------------------------------------------------------------
        # for sending likes by social bhai api
        
        video_likes = self.request.POST.get("your_likes", None)
        admin_id = self.request.POST.get("admin_user_id")
        timezone = self.request.POST.get("timezone")
        video_url = self.request.POST.get("video_url", None)
        user = self.request.user
        if video_likes and video_url:
            YoutubeJob.objects.create(
                user=user,
                video_url=video_url,
                job_type="VIEW_VIDEO",
                status="P",
                view_video=video_likes,
            )
            min_views = os.getenv('MIN_YT_SENT_LIKE_LIMIT')
            url = os.getenv('SOCIALBHAI_URL')
            key = os.getenv('SOCIALBHAI_KEY')
            action_id = os.getenv('SOCIALBHAI_LIKE_ACTION_ID')
            
            parameters = {
                'key' : key,
                'action' : 'add',
                'service' :	action_id,
                'link' :	video_url,
                'quantity' : video_likes,
            }
            response = requests.post(url=url,params=parameters)
            response = response.json()
            if 'status' in response :
                messages.success(request, f"{response['status']}")
            elif 'error' in response :        
                messages.error(request, f"{response['error']}!")
                
        else : 
            messages.error(request, "Video views Job creation Failed!")
        return render(request, self.template_name, self.get_context_data())
        
        
        # ----------------------------------------------------------------------
        
        
        
        
        # ----------------------------------------------------------------------
        # for sending like by own yt accounts and driver
        
        # user_email = self.request.POST.get("youtube_email", None)
        # lik_option = self.request.POST.get("like_video", None)
        # admin_id = self.request.POST.get("admin_user_id")
        # timezone = self.request.POST.get("timezone")
        # user = self.request.user
        # groups = self.request.POST.get("group_name", None)
        # video_url = self.request.POST.get("video_url", None)
        # now = datetime.datetime.now(pytz.timezone("UTC"))
        # try:
        #     if groups and lik_option:
        #         group = YoutubeGroup.objects.get(id=groups)
        #         members = YoutubeAccount.objects.filter(group=group)
        #         job = YoutubeJob.objects.create(
        #             user=user,
        #             video_url=video_url,
        #             job_type="LIKE",
        #             status="P",
        #             group=group,
        #         )
        #         # like_on_video.delay(job.id)
        #         like_video_yt(
        #             job.id, schedule=now, verbose_name=job.job_type, creator=job.user
        #         )
                
        #         messages.success(request, "Like Video Job created Using Group!")
        #         return render(request, self.template_name, self.get_context_data())
        #     elif user_email and lik_option:
        #         youtube_account = YoutubeAccount.objects.filter(id=user_email).first()
        #         job = YoutubeJob.objects.create(
        #             user=user,
        #             video_url=video_url,
        #             job_type="LIKE",
        #             status="P",
        #             accounts=youtube_account,
        #         )
        #         # like_on_video.delay(job.id)
        #         like_video_yt(
        #             job.id, schedule=now, verbose_name=job.job_type, creator=job.user
        #         )
        #         messages.success(request, "Like Video Job created Using Accounts!")
        #         return render(request, self.template_name, self.get_context_data())
        #     else:
        #         messages.error(request, "Select accounts or like checkbox")
        #         return render(request, self.template_name, self.get_context_data())
        # except Exception as e:
        #     print(e)
        #     messages.error(request, "There was an error while creating job.")
        #     return render(request, self.template_name, {})

        # ----------------------------------------------------------------------

class CommentOnYoutubeVideoAPIView(TemplateView):
    template_name = "dashboard/tools/youtube_cmnt.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_accounts = YoutubeAccount.objects.all()
        user_groups = YoutubeGroup.objects.all()
        context["user_accounts"] = user_accounts
        context["user_groups"] = user_groups
        return context

    def post(self, request, *args, **kwargs):
        
        # ----------------------------------------------------
        
        # sending comments by social bhai api.....
        video_comment = self.request.POST.get("your_comment", None)
        admin_id = self.request.POST.get("admin_user_id")
        timezone = self.request.POST.get("timezone")
        video_url = self.request.POST.get("video_url", None)
        comment_list = self.request.POST.get("your_cooment_list", None)
        user = self.request.user
        if video_comment and video_url:
            YoutubeJob.objects.create(
                user=user,
                video_url=video_url,
                job_type="VIEW_VIDEO",
                status="P",
                view_video=video_comment,
            )
            min_views = os.getenv('MIN_YT_SENT_COMMENT_LIMIT')
            url = os.getenv('SOCIALBHAI_URL')
            key = os.getenv('SOCIALBHAI_KEY')
            action_id = os.getenv('SOCIALBHAI_COMMENT_ACTION_ID')
            
            parameters = {
                'key' : key,
                'action' : 'balance'
            }
            # parameters = {
            #     'key' : key,
            #     'action' : 'add',
            #     'service' :	action_id,
            #     'link' :	video_url,
            #     'quantity' : video_comment
            # }
            if comment_list :
                print(type(comment_list))   
                comment_list = str(comment_list).split(',')
                print(type(comment_list))
                parameters['comments'] = comment_list
                if len(comment_list) != int(video_comment) :
                    messages.error(request, f"Please keep comment box empty or enter the same amount of comments as you have enter the needed comments !")
                    return render(request, self.template_name, self.get_context_data()) 
            response = requests.post(url=url,params=parameters)
            response = response.json()
            
            if 'status' in response :
                messages.success(request, f"{response['status']}")
            elif 'error' in response :        
                messages.error(request, f"{response['error']}!")
        else : 
            messages.error(request, "Video views Job creation Failed!")
        return render(request, self.template_name, self.get_context_data()) 
        # -----------------------------------------------------
    
        # -----------------------------------------------------
        
        # using own comments functionality
        # user_email = self.request.POST.get("youtube_email", None)
        # comments = self.request.POST.get("your_cmnt", None)
        # admin_id = self.request.POST.get("admin_user_id")
        # timezone = self.request.POST.get("timezone")
        # user = self.request.user
        # groups = self.request.POST.get("group_name", None)
        # video_url = self.request.POST.get("video_url", None)
        # scheduled_for = datetime.datetime.now(pytz.UTC)
        # now = datetime.datetime.now(pytz.timezone("UTC"))
        # try:
        #     if groups and comments:
        #         group = YoutubeGroup.objects.get(id=groups)
        #         members = YoutubeAccount.objects.filter(group=group)
        #         job = YoutubeJob.objects.create(
        #             user=user,
        #             video_url=video_url,
        #             job_type="COMMENT",
        #             status="P",
        #             group=group,
        #         )
                
        #         comment_video_yt(
        #             job.id, schedule=now, verbose_name=job.job_type, creator=job.user
        #         )
        #         messages.success(request, "Comment on video Job created!")
        #         return render(request, self.template_name, self.get_context_data())
        #     elif user_email and comments:
        #         credential = (
        #             YoutubeAccount.objects.filter(id=user_email).first().credentials
        #         )
        #         youtube_account = YoutubeAccount.objects.filter(id=user_email).first()
        #         job = YoutubeJob.objects.create(
        #             user=user,
        #             video_url=video_url,
        #             job_type="COMMENT",
        #             status="P",
        #             accounts=youtube_account,
        #         )
        #         comment_video_yt(
        #             job.id, schedule=now, verbose_name=job.job_type, creator=job.user
        #         )
        #         messages.success(request, "Comment on video Job created!")
        #         return render(request, self.template_name, self.get_context_data())
        #     else:
        #         messages.error(request, "Please select accounts ")
        #         return render(request, self.template_name, self.get_context_data())
        # except Exception as e:
        #     print(e)
        #     messages.error(request, "There was an error while creating job.")
        #     return render(request, self.template_name, {})
        # -----------------------------------------------------
        


class YoutubeManagerView(TemplateView):
    template_name = "dashboard/viral_ignitor/youtube_account_manager.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_secrets.json"
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            "client_secrets.json",
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/youtube.force-ssl",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
            ],
        )
        flow.redirect_uri = "http://localhost:8000/en/advance/dashboard/youtube_callback/"
        # flow.redirect_uri = os.environ.get("YT_REDIRECT_URL")
        authorization_url, state = flow.authorization_url(
            access_type="offline", approval_prompt="auto", include_granted_scopes="true"
        )
        user_accounts = YoutubeAccount.objects.all()
        context["user_accounts"] = user_accounts
        context["authorization_url"] = authorization_url
        return context


class SubscribeChannelAPIView(TemplateView):
    template_name = "dashboard/tools/subscribe_channel.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_accounts = YoutubeAccount.objects.all()
        user_groups = YoutubeGroup.objects.all()
        context["user_accounts"] = user_accounts
        context["user_groups"] = user_groups
        return context

    def post(self, request, *args, **kwargs):
        # ----------------------------------------------------
        # sending subscribes by social bhai api.....
        video_subscribes = self.request.POST.get("your_subscribes", None)
        admin_id = self.request.POST.get("admin_user_id")
        timezone = self.request.POST.get("timezone")
        video_url = self.request.POST.get("video_url", None)
        user = self.request.user
        if video_subscribes and video_url:
            YoutubeJob.objects.create(
                user=user,
                video_url=video_url,
                job_type="VIEW_VIDEO",
                status="P",
                view_video=video_subscribes,
            )
            min_views = os.getenv('MIN_YT_SENT_SUBSCRIBE_LIMIT')
            url = os.getenv('SOCIALBHAI_URL')
            key = os.getenv('SOCIALBHAI_KEY')
            action_id = os.getenv('SOCIALBHAI_SUBSCRIBE_ACTION_ID')
            
            parameters = {
                'key' : key,
                'action' : 'balance',
                # 'service' :	action_id,
                # 'link' :	video_url,
                # 'quantity' : video_subscribes,
            }
            response = requests.post(url=url,params=parameters)
            response = response.json()
            print(response)
            
            if 'status' in response :
                messages.success(request, f"{response['status']}")
            elif 'error' in response :        
                messages.error(request, f"{response['error']}!")
        else : 
            messages.error(request, "Video views Job creation Failed!")
        return render(request, self.template_name, self.get_context_data())   
        # ----------------------------------------------------
            
        # ----------------------------------------------------
        # sending subscribes by own yt accounts
        
        # user_email = self.request.POST.get("youtube_email", None)
        # subscribe = self.request.POST.get("subscrib_channel", None)
        # admin_id = self.request.POST.get("admin_user_id")
        # channel_id = self.request.POST.get("channel_id")
        # timezone = self.request.POST.get("timezone")
        # user = self.request.user
        # scheduled_for = datetime.datetime.now(pytz.UTC)
        # groups = self.request.POST.get("group_name", None)
        # now = datetime.datetime.now(pytz.timezone("UTC"))
        # try:
        #     if groups and channel_id:
        #         group = YoutubeGroup.objects.get(id=groups)
        #         job = YoutubeJob.objects.create(
        #             user=user,
        #             channel_id=channel_id,
        #             job_type="SUBSCRIBE",
        #             status="P",
        #             group=group,
        #         )
        #         sunscribe_channel_yt(
        #             job.id, schedule=now, verbose_name=job.job_type, creator=job.user
        #         )
        #         messages.success(request, "Comment on video Job created!")
        #         return render(request, self.template_name, self.get_context_data())
        #     elif subscribe and channel_id:
        #         youtube_account = YoutubeAccount.objects.filter(id=user_email).first()
        #         job = YoutubeJob.objects.create(
        #             user=user,
        #             job_type="SUBSCRIBE",
        #             status="P",
        #             channel_id=channel_id,
        #             accounts=youtube_account,
        #         )

        #         sunscribe_channel_yt(
        #             job.id, schedule=now, verbose_name=job.job_type, creator=job.user
        #         )
        #         messages.success(request, "subscribe channel Job creation successfully")
        #         return render(request, self.template_name, self.get_context_data())
        #     else:
        #         messages.error(request, "please select accounts or subscribe button!")
        #         return render(request, self.template_name, self.get_context_data())
        # except Exception as e:
        #     print(e)
        #     messages.error(request, "There was an error while creating job.")
        #     return render(request, self.template_name, {})

        # ----------------------------------------------------

def youtube_callbackurl(request):
    auth_code = request.GET["code"]
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secrets.json"
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        "client_secrets.json",
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/youtube.force-ssl",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ],
    )
    flow.redirect_uri = "http://localhost:8000/en/advance/dashboard/youtube_callback/"
    # flow.redirect_uri = os.environ.get("YT_REDIRECT_URL")
    flow.fetch_token(code=auth_code)
    credentials = flow.credentials
    user_info_service = googleapiclient.discovery.build(
        "oauth2", "v2", credentials=credentials
    )
    user_info = user_info_service.userinfo().get().execute()
    obj = credentials.__dict__
    account = YoutubeAccount.objects.filter(email=user_info["email"])
    if account:
        messages.error(request, "Account already added!")
        return redirect("youtube_manager")
    acc = YoutubeAccount.objects.create(
        email=user_info["email"],
        token=obj["token"],
        credentials=credentials,
        refresh_token=obj["_refresh_token"],
        expiry=obj["expiry"],
    )
    messages.success(request, "Account Added successfully!")

    return redirect("youtube_manager")


class DislikeOnYoutubeVideoAPIView(TemplateView):
    template_name = "dashboard/tools/dislike_video.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_accounts = YoutubeAccount.objects.all()
        user_groups = YoutubeGroup.objects.all()
        context["user_accounts"] = user_accounts
        context["user_groups"] = user_groups
        return context

    def post(self, request, *args, **kwargs):
        user_email = self.request.POST.get("youtube_email", None)
        lik_option = self.request.POST.get("dislike_video", None)
        admin_id = self.request.POST.get("admin_user_id")
        timezone = self.request.POST.get("timezone")
        user = self.request.user
        groups = self.request.POST.get("group_name", None)
        video_url = self.request.POST.get("video_url", None)
        scheduled_for = datetime.datetime.now(pytz.UTC)
        now = datetime.datetime.now(pytz.timezone("UTC"))
        try:
            if groups and lik_option:
                group = YoutubeGroup.objects.get(id=groups)
                job = YoutubeJob.objects.create(
                    user=user,
                    video_url=video_url,
                    job_type="DISLIKE",
                    status="P",
                    group=group,
                )
                dislike_video_yt(
                    job.id, schedule=now, verbose_name=job.job_type, creator=job.user
                )
                messages.success(request, "Like Video Job created!")
                return render(request, self.template_name, self.get_context_data())
            elif user_email and lik_option:
                youtube_account = YoutubeAccount.objects.filter(id=user_email).first()
                job = YoutubeJob.objects.create(
                    user=user,
                    video_url=video_url,
                    job_type="DISLIKE",
                    status="P",
                    accounts=youtube_account,
                )
                # dislike_on_video.delay(job.id)
                dislike_video_yt(
                    job.id, schedule=now, verbose_name=job.job_type, creator=job.user
                )
                messages.success(request, "Dislike Video Job created!")
                return render(request, self.template_name, self.get_context_data())
            else:
                messages.error(request, "Select accounts or dislike checkbox")
                return render(request, self.template_name, self.get_context_data())
        except Exception as e:
            print(e)
            messages.error(request, "There was an error while creating job.")
            return render(request, self.template_name, {})


class ViewsYoutubeVideoAPIView(TemplateView):
    template_name = "dashboard/tools/incres_views.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_accounts = YoutubeAccount.objects.all()
        context["user_accounts"] = user_accounts
        return context

    def post(self, request, *args, **kwargs):
        video_views = self.request.POST.get("your_views", None)
        admin_id = self.request.POST.get("admin_user_id")
        timezone = self.request.POST.get("timezone")
        video_url = self.request.POST.get("video_url", None)
        user = self.request.user
        if video_views and video_url:
            YoutubeJob.objects.create(
                user=user,
                video_url=video_url,
                job_type="VIEW_VIDEO",
                status="P",
                view_video=video_views,
            )
            min_views = os.getenv('MIN_YT_SENT_VIEW_LIMIT')
            url = os.getenv('SOCIALBHAI_URL')
            key = os.getenv('SOCIALBHAI_KEY')
            action_id = os.getenv('SOCIALBHAI_VIEW_ACTION_ID')
            
            # parameters = {
            #     'key' : key,
            #     'action' : 'add',
            #     'service' :	action_id,
            #     'link' :	video_url,
            #     'quantity' : video_views,
            # }
            parameters = {
                'key' : key,
                'action' : 'balance'
            }
            response = requests.post(url=url,params=parameters)
            print(response.json(),': ------------1--------------')
            response = response.json()
            
            if 'status' in response :
                messages.success(request, f"{response['status']}")
            elif 'error' in response :        
                messages.error(request, f"{response['error']}!")
                
            # -------------------------------------------------------------------
            
            # this is used for when we wants to send like throught the chrome driver.
            
            # min_views = 0
            # if int(video_views) < int(min_views) : 
            #     messages.error(request, f"Please send views more than {min_views} !")
            # else : 
                # send_view(video_url=video_url,video_views=video_views)
            #     messages.success(request, "Video views Job created!")
            
            # -------------------------------------------------------------------
        else : 
            messages.error(request, "Video views Job creation Failed!")
        return render(request, self.template_name, self.get_context_data())


class VideoUploadOnYoutubeAPIView(TemplateView):
    template_name = "dashboard/tools/upload_video.html"

    def move_file_to_s3(self, file, file_path, bucket_name=None):
        if not bucket_name:
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        bucket_resource = s3
        resp = bucket_resource.upload_file(
            Bucket=bucket_name,
            Filename=file,
            Key=file_path,
            ExtraArgs={"ACL": "public-read"},
        )
        return resp

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_accounts = YoutubeAccount.objects.filter(user=user)
        context["user_accounts"] = user_accounts
        return context

    def post(self, request, *args, **kwargs):
        user_email = self.request.POST.get("youtube_email", None)
        channel_id = self.request.POST.get("channel_id", None)
        admin_id = self.request.POST.get("admin_user_id")
        files = {"video": self.request.FILES["video_id"]}
        title = self.request.POST.get("title", None)
        description = self.request.POST.get("description", None)
        timezone = self.request.POST.get("timezone")
        user = self.request.user

        temp_file = files["video"].name
        with open(temp_file, "wb+") as f:
            for chunk in files["video"].chunks():
                f.write(chunk)
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        file_path = "/surviral_web/post_image/" + files["video"].name
        temp_file_path = os.path.join(os.getcwd(), files["video"].name)
        self.move_file_to_s3(
            file=temp_file_path, file_path=file_path, bucket_name=bucket_name
        )

        credential = YoutubeAccount.objects.filter(id=user_email).first().credentials
        if channel_id and credential:
            obj = video_upload(credential, channel_id, temp_file, title, description)
            if obj:
                messages.success(request, "Dislike Video Job created!")
                return render(request, self.template_name, self.get_context_data())
            else:
                messages.error(request, "Dislike Video Job creation Failed!")
                return render(request, self.template_name, self.get_context_data())
        messages.error(request, "Dislike Video Job creation Failed!")
        return render(request, self.template_name, self.get_context_data())


class YoutubeGroupManagerView(TemplateView):
    template_name = "dashboard/viral_ignitor/youtube_group_manager.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["groups"] = self.request.user.youtubegroup_set.all()
        context["youtube_accounts"] = YoutubeAccount.objects.filter(
            group__in=context["groups"]
        )
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        account = YoutubeAccount.objects.filter(id=self.kwargs.get("youtube_id"))
        if account.exists():
            rm_group = YoutubeAccount.objects.get(id=self.kwargs.get("youtube_id"))
            rm_group.group = None
            rm_group.save()
            messages.success(request, "Instagram Account Remove successfully!")
            return redirect("youtube_group_manager")
        return render(request, self.template_name, context)


class CreateYoutubeGroup(TemplateView):
    template_name = "dashboard/viral_ignitor/create_youtube_group.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request):
        context = self.get_context_data()
        data = self.request.POST
        group_name = data.get("group_name")
        description = data.get("description")

        if group_name and description:
            user_group = YoutubeGroup.objects.create(
                name=group_name, user=self.request.user, desc=description
            )
            messages.success(request, "Group have been added successfully.")
            return redirect("youtube_group_manager")
        return render(request, self.template_name, context)


class LinkToYoutubeGroupView(TemplateView):
    template_name = "dashboard/viral_ignitor/link_youtube_account.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["groups"] = self.request.user.youtubegroup_set.all()
        context["current_group"] = self.request.user.youtubegroup_set.first()
        context["list_insta"] = self.request.user.youtubegroup_set.filter(
            id=int(self.kwargs.get("group_id"))
        ).first()
        context["account"] = YoutubeAccount.objects.filter(group=context["list_insta"])
        context["accounts"] = YoutubeAccount.objects.filter(group__isnull=True)

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        data = self.request.POST
        group_id = data.get("insta_group_id")
        insta_ids = data.getlist("insta_account")
        user = request.user
        if not insta_ids:
            messages.error(request, "please select instagram accounts")
            return redirect("youtube_group_manager")
        try:
            user_account_qs = user.youtubegroup_set.filter(id=group_id).first()
        except:
            user_account_qs = None
        if user_account_qs:
            for insta_id in insta_ids:
                user_account = YoutubeAccount.objects.get(id=insta_id)

                user_account.group = user_account_qs
                user_account.save()
            messages.success(request, "Group link successfully.")
            return redirect("youtube_group_manager")

        messages.error(request, "Group does not exists.")
        return redirect("youtube_group_manager")


class ListYoutubeAccountView(TemplateView):
    template_name = "dashboard/viral_ignitor/youtube_group_manager.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["groups"] = self.request.user.youtubegroup_set.all()
        context["list_insta"] = self.request.user.youtubegroup_set.filter(
            id=int(self.kwargs.get("group_id"))
        )
        context["youtube_accounts"] = YoutubeAccount.objects.filter(
            group__in=context["list_insta"]
        )
        context["group_name"] = (
            self.request.user.youtubegroup_set.filter(
                id=int(self.kwargs.get("group_id"))
            )
            .first()
            .name
        )
        return context


class DeleteYoutubeGroupView(TemplateView):
    template_name = "dashboard/viral_ignitor/link_youtube_account.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["groups"] = self.request.user.youtubegroup_set.all()
        context["current_group"] = self.request.user.youtubegroup_set.first()
        context["list_insta"] = self.request.user.youtubegroup_set.filter(
            id=self.kwargs.get("group_id")
        ).first()
        context["account"] = YoutubeAccount.objects.filter(group=context["list_insta"])
        context["accounts"] = YoutubeAccount.objects.filter(group__isnull=True)

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        account = request.user.youtubegroup_set.filter(id=self.kwargs.get("group_id"))
        if account.exists():
            rm_group = YoutubeGroup.objects.get(id=self.kwargs.get("group_id"))
            rm_group.delete()
            messages.success(request, "Youtube Group Delete successfully!")
            return redirect("youtube_group_manager")
        return render(request, self.template_name, context)


class EditJobView(TemplateView):
    template_name = "dashboard/viral_ignitor/edit_job.html"

    def move_file_to_s3(self, file, file_path, bucket_name=None):
        if not bucket_name:
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        bucket_resource = s3
        resp = bucket_resource.upload_file(
            Bucket=bucket_name,
            Filename=file,
            Key=file_path,
            ExtraArgs={"ACL": "public-read"},
        )
        return resp

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job_id = self.kwargs.get("job_id")
        user = self.request.user
        jobs = Job.objects.filter(id=job_id).first()
        context["commment"] = jobs.data["comment"]
        context["caption"] = jobs.data["caption"]
        context["image"] = jobs.data["file_name"]
        user_groups = SurviralGroup.objects.filter(user=user)
        context["user_groups"] = user_groups
        context["jobs"] = jobs
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": bucket_name,
                "Key": jobs.data["file_path"],
            },
        )
        context["image"] = url
        return context

    def post(self, request, **kwargs):
        insta_acc_id = self.request.POST["insta_user_id"]
        job_id = self.kwargs.get("job_id")
        caption = self.request.POST["caption"]
        comment = self.request.POST.get("comment")
        scheduled_time = self.request.POST["time_post"]
        files = {"image": self.request.FILES["post-img"]}
        save_draft = self.request.POST.get("save_draft", False)
        group = self.request.POST.get("group", None)
        user = self.request.user

        temp_file = files["image"].name
        with open(temp_file, "wb+") as f:
            for chunk in files["image"].chunks():
                f.write(chunk)
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        file_path = "/surviral_web/post_image/" + files["image"].name
        temp_file_path = os.path.join(os.getcwd(), files["image"].name)
        self.move_file_to_s3(
            file=temp_file_path, file_path=file_path, bucket_name=bucket_name
        )
        if int(save_draft) == 1:
            save_draft = True
        if group:
            group_accounts = UserAccount.objects.filter(group=group)
        else:
            group_accounts = None
        scheduled_for = parse(scheduled_time)
        scheduled_for = tz.make_aware(
            scheduled_for, pytz.timezone(self.request.user.timezone)
        )
        caption = caption.replace('"', "").replace("'", "")
        comment = comment.replace('"', "").replace("'", "")
        try:
            image_name = files["image"].name
            account = UserAccount.objects.get(id=insta_acc_id)

            Job.objects.filter(id=job_id).update(
                user_account=account,
                job_type="POST",
                is_draft=save_draft,
                data={
                    "caption": caption,
                    "comment": comment,
                    "file_name": image_name,
                    "file_path": file_path,
                },
            )
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            messages.success(request, "Post Job Updated!")
        except Exception as e:
            print(e)
            messages.error(request, "There was an error while Updated job.")
        return render(request, self.template_name, self.get_context_data())


class MultiFollowEditAPIView(TemplateView):
    template_name = "dashboard/tools/edit_multifollow.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_groups = SurviralGroup.objects.filter(user=user)
        context["user_groups"] = user_groups
        job_id = self.kwargs.get("job_id")
        jobs = Job.objects.filter(id=job_id).first()
        context["target_username"] = jobs.data["target_username"]
        context["times"] = jobs.data["times"]
        context["scheduled_for"] = jobs.scheduled_for
        context["jobs"] = jobs

        return context

    def post(self, request, *args, **kwargs):
        removed_users = []
        target_user = self.request.POST.get("follow_multiple_users", None)
        target_user = target_user.split(",")
        number_of_followers = self.request.POST.get("number_of_followers")
        schedule_time = self.request.POST.get("scheduled_time")
        user_account_id = self.request.POST.get("insta_user_id")
        timezone = self.request.POST.get("timezone")
        job_id = self.kwargs.get("job_id")
        """
        Check boxes
        """
        lik_cmnt_opt = True if self.request.POST.get("lk_cmnt_flw", None) else False
        not_followed_back = (
            True if self.request.POST.get("not_followed_back", None) else False
        )
        followed_back = True if self.request.POST.get("followed_back", None) else False
        group = self.request.POST.get("group", None)
        if group:
            group_accounts = UserAccount.objects.filter(group=group)
        else:
            group_accounts = None

        account = UserAccount.objects.get(id=int(user_account_id))
        if int(number_of_followers) > 20:
            messages.error(request, "Please enter less or equal 20 follows.")
            return render(request, self.template_name, self.get_context_data())

        if len(target_user):
            scheduled_for = parse(schedule_time)
            scheduled_for = tz.make_aware(scheduled_for, pytz.timezone(timezone))
            Job.objects.filter(id=job_id).update(
                user_account=account,
                scheduled_for=scheduled_for,
                timezone=timezone,
                data={
                    "target_username": ",".join(target_user),
                    "times": number_of_followers,
                },
                like_comment=lik_cmnt_opt,
                other_acc_not_followed_back=not_followed_back,
                other_acc_followed_back=followed_back,
            )
            messages.success(request, "Multi Follow Job Updated!")

        if len(removed_users):
            removed = ",".join(removed_users)
            messages.error(
                request,
                f"Job pending for provided usernames please wait or Provide other then these usernames: {removed}",
            )

        return render(request, self.template_name, self.get_context_data())


class EditGiveYourCmntAPIView(TemplateView):
    template_name = "dashboard/tools/edit_manual_cmnt.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_groups = SurviralGroup.objects.filter(user=user)
        job_id = self.kwargs.get("job_id")
        jobs = Job.objects.filter(id=job_id).first()
        context["target_username"] = jobs.data["target_username"]
        context["comment"] = jobs.data["comment"]
        context["user_groups"] = user_groups
        return context

    def post(self, request, *args, **kwargs):
        insta_user = self.request.POST.get("insta_username", None)
        cmnt = self.request.POST.get("your_cmnt", None)
        admin_id = self.request.POST.get("admin_user_id")
        user_account_id = self.request.POST.get("insta_user_id")
        timezone = self.request.POST.get("timezone")
        group = self.request.POST.get("group", None)
        user = self.request.user
        job_id = self.kwargs.get("job_id")
        scheduled_for = datetime.datetime.now(pytz.UTC)
        if group:
            group_accounts = UserAccount.objects.filter(group=group)
        else:
            group_accounts = None
        if group_accounts:
            for account in group_accounts:
                if account.login_status == "IN":
                    Job.objects.filter(id=job_id).update(
                        user_account=account,
                        job_type="CMNT_TARGET_POST",
                        job_title="Comment on post of target user",
                        app_type="IG",
                        image=None,
                        scheduled_for=scheduled_for,
                        timezone=timezone,
                        status="P",
                        data={"target_username": insta_user, "comment": cmnt},
                    )
        else:
            account = UserAccount.objects.get(id=user_account_id)
            Job.objects.filter(id=job_id).update(
                user_account=account,
                job_type="CMNT_TARGET_POST",
                job_title="Comment on post of target user",
                app_type="IG",
                image=None,
                scheduled_for=scheduled_for,
                timezone=timezone,
                status="P",
                data={"target_username": insta_user, "comment": cmnt},
            )
        messages.success(request, "Like or Comment on Followings Post Job created!")
        return render(request, self.template_name, self.get_context_data())


class EditSingleFollowAPIView(TemplateView):
    template_name = "dashboard/tools/edit_single_follow.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_groups = SurviralGroup.objects.filter(user=user)
        job_id = self.kwargs.get("job_id")
        jobs = Job.objects.filter(id=job_id).first()
        context["target_user"] = jobs.data["target_user"]
        context["user_groups"] = user_groups
        return context

    def post(self, request, *args, **kwargs):
        target_user = self.request.POST.get("follow_username", None)
        user_id = self.request.POST.get("insta_user_id")
        timezone = self.request.POST.get("timezone", "Asia/Kolkata")
        user = self.request.user
        group = self.request.POST.get("group", None)
        job_id = self.kwargs.get("job_id")
        scheduled_for = datetime.datetime.now(pytz.UTC)
        if group:
            group_accounts = UserAccount.objects.filter(group=group)
        else:
            group_accounts = None

        if group_accounts:
            for account in group_accounts:
                if account.login_status == "IN":
                    Job.objects.filter(id=job_id).update(
                        user_account=account,
                        job_type="USERNAME_FOLLOW",
                        job_title="Follow Single User",
                        app_type="IG",
                        timezone=timezone,
                        scheduled_for=scheduled_for,
                        status="P",
                        data={"target_user": target_user},
                    )
            messages.success(request, "Follow Job Updated!")
            return render(request, self.template_name, self.get_context_data())
        else:
            account = UserAccount.objects.get(id=user_id)
            Job.objects.filter(id=job_id).update(
                user_account=account,
                job_type="USERNAME_FOLLOW",
                job_title="Follow Single User",
                app_type="IG",
                timezone=timezone,
                scheduled_for=scheduled_for,
                status="P",
                data={"target_user": target_user},
            )
            return render(request, self.template_name, self.get_context_data())


class EditLikeCmntOnFollowerPostAPIView(TemplateView):
    template_name = "dashboard/tools/edit_like_cmnt_followers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_groups = SurviralGroup.objects.filter(user=user)
        job_id = self.kwargs.get("job_id")
        jobs = Job.objects.filter(id=job_id).first()
        context["like"] = jobs.data["like"]
        context["comment"] = jobs.data["comment"]
        context["target_username"] = jobs.data["target_username"]
        context["user_groups"] = user_groups
        return context

    def post(self, request, *args, **kwargs):
        insta_user = self.request.POST.get("insta_username", None)
        lik_option = self.request.POST.get("like_post", None)
        cmnt_option = self.request.POST.get("cmnt_post", None)
        admin_id = self.request.POST.get("admin_user_id")
        user_account_id = self.request.POST.get("insta_user_id")
        timezone = self.request.POST.get("timezone")
        group = self.request.POST.get("group", None)
        user = self.request.user
        job_id = self.kwargs.get("job_id")
        scheduled_for = datetime.datetime.now(pytz.UTC)

        if group:
            group_accounts = UserAccount.objects.filter(group=group)
        else:
            group_accounts = None
        account = UserAccount.objects.get(id=user_account_id)
        Job.objects.filter(id=job_id).update(
            user_account=account,
            data={
                "target_username": insta_user,
                "like": lik_option,
                "comment": cmnt_option,
            },
        )

        messages.success(request, "Like or Comment on Followings Post Job created!")
        return render(request, self.template_name, self.get_context_data())


class EditHashTagsLikeView(TemplateView):
    template_name = "dashboard/tools/edit_hashtags_like.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['user_accounts'] = self.request.user.useraccount_set.all()
        user = self.request.user
        user_groups = SurviralGroup.objects.filter(user=user)
        context["user_groups"] = user_groups
        job_id = self.kwargs.get("job_id")
        jobs = Job.objects.filter(id=job_id).first()
        context["hashtag"] = jobs.data["hashtag"]
        context["num_of_likes"] = jobs.data["num_of_likes"]
        return context

    def post(self, request, *args, **kwargs):
        group = self.request.POST.get("group", None)
        user = self.request.user
        hashtags = request.POST.get("hashtags")
        num_posts_like = request.POST.get("post_counts")
        timezone = self.request.POST.get("timezone")
        scheduled_for = datetime.datetime.now(pytz.UTC)
        job_id = self.kwargs.get("job_id")

        if group:
            group_accounts = UserAccount.objects.filter(group=group)
        else:
            group_accounts = None

        insta_user_id = self.request.POST.get("insta_user_id")
        account = UserAccount.objects.get(id=insta_user_id)
        Job.objects.filter(id=job_id).update(
            user_account=account,
            status="P",
            data={"num_of_likes": num_posts_like, "hashtag": hashtags},
        )

        messages.success(request, "Like with hashtag Job Updated!")
        return render(request, self.template_name, self.get_context_data())


class EditLikeCmntOnPostAPIView(TemplateView):
    template_name = "dashboard/tools/edit_like_cmnt.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_groups = SurviralGroup.objects.filter(user=user)
        context["user_groups"] = user_groups
        job_id = self.kwargs.get("job_id")
        jobs = Job.objects.filter(id=job_id).first()
        context["like"] = jobs.data["like"]
        context["comment"] = jobs.data["comment"]
        context["target_username"] = jobs.data["target_username"]
        return context

    def post(self, request, *args, **kwargs):
        insta_user = self.request.POST.get("insta_username", None)
        lik_option = self.request.POST.get("like_post", None)
        cmnt_option = self.request.POST.get("cmnt_post", None)
        admin_id = self.request.POST.get("admin_user_id")
        user_account_id = self.request.POST.get("insta_user_id")
        timezone = self.request.POST.get("timezone")
        group = self.request.POST.get("group", None)
        job_id = self.kwargs.get("job_id")
        user = self.request.user
        scheduled_for = datetime.datetime.now(pytz.UTC)

        # Create jobs for all accounts in a group
        if group:
            group_accounts = UserAccount.objects.filter(group=group)
        else:
            group_accounts = None
        account = UserAccount.objects.get(id=user_account_id)
        Job.objects.filter(id=job_id).update(
            user_account=account,
            data={
                "target_username": insta_user,
                "like": lik_option,
                "comment": cmnt_option,
            },
        )
        messages.success(request, "Like or Comment on Post Job updated!")
        return render(request, self.template_name, self.get_context_data())


class EditHashtagsFollowView(TemplateView):
    template_name = "dashboard/tools/edit_hashtags_follow.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_groups = SurviralGroup.objects.filter(user=user)
        context["user_groups"] = user_groups
        job_id = self.kwargs.get("job_id")
        jobs = Job.objects.filter(id=job_id).first()
        context["hashtag"] = jobs.data["hashtag"]
        context["num_of_accounts_to_follow"] = jobs.data["num_of_accounts_to_follow"]
        return context

    def post(self, request, *args, **kwargs):
        insta_user_id = self.request.POST.get("insta_user_id")
        user = self.request.user
        timezone = self.request.POST.get("timezone", "Asia/Kolkata")
        hashtags = self.request.POST.get("hashtags")
        number_of_follows = self.request.POST.get("follows", 0)
        job_id = self.kwargs.get("job_id")

        account = UserAccount.objects.get(id=insta_user_id)
        Job.objects.filter(id=job_id).update(
            user_account=account,
            status="P",
            data={"num_of_accounts_to_follow": number_of_follows, "hashtag": hashtags},
        )

        messages.success(request, "Follow with hashtag Job updated!")
        return render(request, self.template_name, self.get_context_data())


class EditLikeCmntOnFollowingPostAPIView(TemplateView):
    template_name = "dashboard/tools/edit_like_cmnt_followings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_groups = SurviralGroup.objects.filter(user=user)
        context["user_groups"] = user_groups
        job_id = self.kwargs.get("job_id")
        jobs = Job.objects.filter(id=job_id).first()
        context["like"] = jobs.data["like"]
        context["comment"] = jobs.data["comment"]
        context["target_username"] = jobs.data["target_username"]
        return context

    def post(self, request, *args, **kwargs):
        insta_user = self.request.POST.get("insta_username", None)
        lik_option = self.request.POST.get("like_post", None)
        cmnt_option = self.request.POST.get("cmnt_post", None)
        admin_id = self.request.POST.get("admin_user_id")
        user_account_id = self.request.POST.get("insta_user_id")
        timezone = self.request.POST.get("timezone")
        group = self.request.POST.get("group", None)
        user = self.request.user
        job_id = self.kwargs.get("job_id")
        scheduled_for = datetime.datetime.now(pytz.UTC)

        account = UserAccount.objects.get(id=user_account_id)
        Job.objects.filter(id=job_id).update(
            user_account=account,
            data={
                "target_username": insta_user,
                "like": lik_option,
                "comment": cmnt_option,
            },
        )

        messages.success(request, "Like or Comment on Followings Post Job Updated!")
        return render(request, self.template_name, self.get_context_data())


class EditsPostStoryView(TemplateView):
    template_name = "dashboard/viral_ignitor/edit_create_story.html"

    def move_file_to_s3(self, file, file_path, bucket_name=None):
        if not bucket_name:
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        bucket_resource = s3
        resp = bucket_resource.upload_file(
            Bucket=bucket_name,
            Filename=file,
            Key=file_path,
            ExtraArgs={"ACL": "public-read"},
        )
        return resp

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        job_id = self.kwargs.get("job_id")
        jobs = Job.objects.filter(id=job_id).first()
        context["file_name"] = jobs.data["file_name"]
        context["file_path"] = jobs.data["file_path"]

        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": bucket_name,
                "Key": jobs.data["file_path"]["file_path_0"],
            },
        )
        context["image"] = url
        return context

    def post(self, request, **kwargs):
        insta_acc_id = self.request.POST["insta_user_id"]
        caption = self.request.POST.get("caption", "")
        scheduled_time = self.request.POST["time_post"]
        user_id = self.request.POST["user"]
        # files = {'image': self.request.FILES['post-stry']}
        save_draft = request.POST.get("save_draft", False)
        # url = URL + 'image_post/'
        job_id = self.kwargs.get("job_id")
        if int(save_draft) == 1:
            save_draft = True

        files = self.request.FILES
        multi_dict = files.getlist("post-stry")
        files_name = {}
        files_path = {}
        for file, i in zip(multi_dict, range(len(multi_dict))):
            temp_file = file.name
            files_name.update({f"image_{i}": file.name})
            with open(temp_file, "wb+") as f:
                for chunk in file.chunks():
                    f.write(chunk)
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            file_path = "/surviral_web/post_image/" + file.name
            files_path.update({f"file_path_{i}": file_path})
            temp_file_path = os.path.join(os.getcwd(), file.name)
            self.move_file_to_s3(
                file=temp_file_path, file_path=file_path, bucket_name=bucket_name
            )

        timezone = self.request.POST.get("timezone")
        scheduled_for = parse(scheduled_time)
        scheduled_for = tz.make_aware(scheduled_for, pytz.timezone(timezone))
        try:
            data = {
                "user": int(user_id),
                "insta_acc_id": int(insta_acc_id),
                "caption": caption,
                "scheduled_time": scheduled_time,
                "file_name": files_name,
                "file_path": files_path,
            }
            username = User.objects.get(pk=user_id)
            user_account = UserAccount.objects.filter(id=insta_acc_id).first()
            job = Job.objects.filter(id=job_id).update(
                user=username,
                data=data,
            )

            # Get device of the user account
            try:
                device = Device.objects.filter(accounts=user_account).first()

                if not device:
                    all_devices = Device.objects.all()
                    if len(all_devices) > 0:
                        device = random.choice(all_devices)
                        device.accounts.add(user_account)
                        device.save()

                JobQueue.objects.create(job=job, status="P", device=device)
            except Exception as e:
                print(e)
                messages.error(request, "There was an error while updating job.")
                return render(request, self.template_name, self.get_context_data())

            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

            messages.success(request, "Post Job updated!")
        except Exception as e:
            print(e)
            messages.error(request, "There was an error while updating job.")

        return render(request, self.template_name, {})
