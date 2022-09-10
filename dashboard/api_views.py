from dateutil.parser import parse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from instabot.models import *

User = get_user_model()


class CheckLoginStatus(APIView):
    def post(self, request):
        try:
            ac_qs = request.user.useraccount_set.filter(id=self.request.data.get("uid"))
            if ac_qs.exists():
                data = ac_qs.first().login_status
            else:
                data = False
        except:
            data = False
        return Response({"data": data}, status=status.HTTP_200_OK)


class ActivityFilter(APIView):
    def post(self, request):
        resp_data = []
        data = request.data
        search_keyword = data.get("search_keyword", None)
        date = data.get("date", None)
        sort_by = data.get("sort_by", None)
        filter_status = data.get("filter_status", None)
        useraccount_id = data.get("uid")
        user_account_qs = UserAccount.objects.filter(id=useraccount_id)
        if user_account_qs.exists():
            job_qs = user_account_qs.first().job_set.filter()
            if search_keyword:
                job_qs = job_qs.filter(job_title__icontains=search_keyword)
            if date:
                parsed_date = parse(date)
                job_qs = job_qs.filter(scheduled_for__date=parsed_date.date())
            if filter_status:
                job_qs = job_qs.filter(status=filter_status)
            if sort_by:
                if sort_by == "title":
                    key = "job_title"
                else:
                    key = "scheduled_for"
                job_qs = job_qs.order_by(key)
            resp_data = self.get_serialized(job_qs)
        return Response(resp_data, status=status.HTTP_200_OK)

    def get_serialized(self, job_qs):
        resp_data = []
        for job in job_qs:
            resp_data.append(
                {
                    "date": job.scheduled_for.strftime("%d"),
                    "month_year": job.scheduled_for.strftime("%b %Y"),
                    "title": job.job_title,
                }
            )
        return resp_data


class UserAccountAutoStatus(APIView):
    def get(self, request):
        data = request.GET
        uid = data.get("uid")
        user_account_qs = UserAccount.objects.filter(id=uid)
        if user_account_qs.exists():
            auto_status = user_account_qs.first().automation
        else:
            auto_status = 0

        return Response(auto_status)

    def post(self, request):
        data = request.data
        uid = data.get("uid")
        status = data.get("status")
        user_account_qs = UserAccount.objects.filter(id=uid)
        if user_account_qs.exists() and status:
            automation = True if status == "1" else False
            user_account_qs.update(automation=automation)

        return Response(automation)


class GetUserAccountDetails(APIView):
    def post(self, request):
        data = request.data
        uid = data.get("uid")
        resp_data = {}
        user_account_qs = UserAccount.objects.filter(id=uid)

        if user_account_qs.exists():
            job_qs = user_account_qs.first().job_set.filter(status="C")
            likes = sum(
                [
                    int(job.data.get("num_of_likes", 0))
                    for job in job_qs.filter(job_type="LIKE_MULTIPLE_POSTS")
                ]
            )
            follows = sum(
                [
                    int(job.data.get("times", 0))
                    for job in job_qs.filter(job_type="MULTI_USER_FOLLOW")
                ]
            )
            unfollows = sum(
                [
                    int(job.data.get("times", 0))
                    for job in job_qs.filter(job_type="AUTO_UNFOLLOW")
                ]
            )
            post_image = job_qs.filter(job_type="POST").count()

            resp_data = {
                "likes": likes,
                "follows": follows,
                "unfollows": unfollows,
                "post_image": post_image,
            }
        return Response(resp_data, status=status.HTTP_200_OK)
