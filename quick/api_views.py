import requests
import json
import datetime
from dateutil.parser import parse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from instabot.models import *
from django.conf import settings

User = get_user_model()
URL = settings.INSTABOT_URL
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name="dispatch")
class SearchInstagramUserAccount(APIView):
    def get(self, request):
        username = request.GET.get("search")
        id = 0
        results = []
        api_resp = requests.get(
            f"https://www.instagram.com/web/search/topsearch/?query={username}"
        )
        try:
            users = json.loads(api_resp.content.decode("utf-8"))["users"]
            for user in users:
                id += 1
                results.append(
                    {"id": user["user"]["username"], "text": user["user"]["username"]}
                )
            resp = {
                "results": results,
            }
        except:
            resp = {"results": []}
        return Response(resp, status=status.HTTP_200_OK)


class CheckQuickLoginStatus(APIView):
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


class GetDecodedString(APIView):
    def get(self, request):
        string = self.request.GET.get("string")
        if type(string) == str:
            resp = string.encode("utf-16", "surrogatepass").decode("utf-16")
        elif type(string) == bytes:
            resp = (
                string.decode("utf-8")
                .encode("utf-16", "surrogatepass")
                .decode("utf-16")
            )
        else:
            resp = string
        return Response({"data": resp}, status=status.HTTP_200_OK)
