import os
import boto3
import pytz
import datetime
from django.views.generic import TemplateView, CreateView
from twitterbot.models import TwitterAccount,TwitterJob, TwitterUser
from twitterbot.task import *
from django.contrib import messages
from django.shortcuts import render, redirect
from django.conf import settings



class FollowAPIView(TemplateView):
    template_name = "dashboard/tools/twitter_follow.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_accounts = TwitterAccount.objects.filter(user=user)
        context["user_accounts"] = user_accounts
        return context

    def post(self, request, *args, **kwargs):
        user_email = self.request.POST.get("user_email", None)
        follow = self.request.POST.get("follow", None)
        admin_id = self.request.POST.get("admin_user_id")
        timezone = self.request.POST.get("timezone")
        user = self.request.user
        now = datetime.datetime.now(pytz.timezone("UTC"))
        username = self.request.POST.get("username", None)
        try:
            if user_email and follow:
                twitter_account = TwitterAccount.objects.filter(id=user_email).first()
                job = TwitterJob.objects.create(
                    user=user,
                    job_type="FOLLOW",
                    status="P",
                    accounts=twitter_account,
                    follow_user=username
                )
                # user_follow(
                #     job.id, username, schedule=now, verbose_name=job.job_type, creator=job.user
                # )
                messages.success(request, "Follow user job created Using Accounts!")
                return render(request, self.template_name, self.get_context_data())
            else:
                messages.error(request, "Select accounts or follow checkbox")
                return render(request, self.template_name, self.get_context_data())
        except Exception as e:
            print(e)
            messages.error(request, "There was an error while creating job.")
            return render(request, self.template_name, {})


class MultipleFollowAPIView(TemplateView):
    template_name = "dashboard/tools/twitter_multiplefollow.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_accounts = TwitterAccount.objects.filter(user=user)
        context["user_accounts"] = user_accounts
        return context

    def post(self, request, *args, **kwargs):
        user_email = self.request.POST.get("user_email", None)
        follow = self.request.POST.get("follow", None)
        admin_id = self.request.POST.get("admin_user_id")
        timezone = self.request.POST.get("timezone")
        user = self.request.user
        now = datetime.datetime.now(pytz.timezone("UTC"))
        username = self.request.POST.get("follow_multiple_users", None)
        number_of_follow = int(self.request.POST.get("number_of_followers", None))
        try:
            if user_email and username:
                twitter_account = TwitterAccount.objects.filter(id=user_email).first()
                job = TwitterJob.objects.create(
                    user=user,
                    job_type="MULTIPLE_FOLLOW",
                    status="P",
                    accounts=twitter_account,
                    follow_user=username
                )
                get_followers(
                  username, schedule=now, verbose_name=job.job_type, creator=job.user
                )
                messages.success(request, "Follow user job created Using Accounts!")
                return render(request, self.template_name, self.get_context_data())
            else:
                messages.error(request, "Select accounts")
                return render(request, self.template_name, self.get_context_data())
        except Exception as e:
            print(e)
            messages.error(request, "There was an error while creating job.")
            return render(request, self.template_name, {})


class RetweetAPIView(TemplateView):
    template_name = "dashboard/tools/retweet.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_accounts = TwitterAccount.objects.filter(user=user)
        context["user_accounts"] = user_accounts
        return context

    def post(self, request, *args, **kwargs):
        user_email = self.request.POST.get("user_email", None)
        follow = self.request.POST.get("follow", None)
        admin_id = self.request.POST.get("admin_user_id")
        timezone = self.request.POST.get("timezone")
        user = self.request.user
        now = datetime.datetime.now(pytz.timezone("UTC"))
        username = self.request.POST.get("user_retweet", None)
        try:
            if user_email and username:
                twitter_account = TwitterAccount.objects.filter(id=user_email).first()
                trg_user, _ = TwitterUser.objects.get_or_create(username=username)
                job = TwitterJob.objects.create(
                    user=user,
                    job_type="RETWEET",
                    status="P",
                    twitter_account=twitter_account,
                    follow_user=username
                )
                job.target_username.add(trg_user)
                messages.success(request, "Targeted user retweet job created Using Accounts!")
                return render(request, self.template_name, self.get_context_data())
            else:
                messages.error(request, "Select accounts")
                return render(request, self.template_name, self.get_context_data())
        except Exception as e:
            print(e)
            messages.error(request, "There was an error while creating job.")
            return render(request, self.template_name, {})


class TweetView(TemplateView):
    template_name = "dashboard/viral_ignitor/post_on_twitter.html"

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
        user_accounts = TwitterAccount.objects.filter(user=user)
        context["user_accounts"] = user_accounts
        return context

    def post(self, request, **kwargs):
        twitter_ac_id = self.request.POST["accounts"]
        msg = self.request.POST["tweet_text"]
        group = self.request.POST.get("group", None)
        user = self.request.user
        file_path = None
        temp_file_path = None
        try:
            files = {"image": self.request.FILES["post-img"]}
        except:
            files = None
        if files:
            temp_file = files["image"].name
            with open(temp_file, "wb+") as f:
                for chunk in files["image"].chunks():
                    f.write(chunk)
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            file_path = "/surviral_web/tweet/" + files["image"].name
            temp_file_path = os.path.join(os.getcwd(), files["image"].name)
            self.move_file_to_s3(
                file=temp_file_path, file_path=file_path, bucket_name=bucket_name
            )
        else:
            file_path = None

        if group:
            group_accounts = TwitterAccount.objects.filter(group=group)
        else:
            group_accounts = None
       
        try:
            account = TwitterAccount.objects.get(id=twitter_ac_id)
            TwitterJob.objects.create(
                user=user,
                twitter_account=account,
                job_type="TWEET",
                status="P",
                image_path=file_path,
                text_message=msg,
            )
            if temp_file_path:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            messages.success(request, "Tweet Job Created!")
        except Exception as e:
            print(e)
            messages.error(request, "There was an error while creating job.")
        return render(request, self.template_name, self.get_context_data())


class LikeOnTweetAPIView(TemplateView):
    template_name = "dashboard/tools/like_on_tweet.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_accounts = TwitterAccount.objects.filter(user=user)
        context["user_accounts"] = user_accounts
        return context

    def post(self, request, *args, **kwargs):
        user_email = self.request.POST.get("user_email", None)
        timezone = self.request.POST.get("timezone")
        user = self.request.user
        now = datetime.datetime.now(pytz.timezone("UTC"))
        username = self.request.POST.get("like_tweet", None)
        try:
            if user_email and username:
                twitter_account = TwitterAccount.objects.filter(id=user_email).first()
                trg_user, _ = TwitterUser.objects.get_or_create(username=username)
                job = TwitterJob.objects.create(
                    user=user,
                    job_type="LIKE",
                    status="P",
                    twitter_account=twitter_account,
                    follow_user=username
                )
                job.target_username.add(trg_user)
                messages.success(request, "Targeted user retweet job created Using Accounts!")
                return render(request, self.template_name, self.get_context_data())
            else:
                messages.error(request, "Select accounts")
                return render(request, self.template_name, self.get_context_data())
        except Exception as e:
            print(e)
            messages.error(request, "There was an error while creating job.")
            return render(request, self.template_name, {})
