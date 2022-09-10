import datetime

import pytz
from django.contrib import messages
from django.shortcuts import render
from rest_framework.views import APIView
from telegram_bot.models import *
from rest_framework.response import Response
# Create your views here.
from django.views.generic import TemplateView, CreateView


# Create your views here.
from telegram_bot.utils import TelegramUtilities


class AutoDirectMessageView(TemplateView):
    template_name = "dashboard/tools/telegram_auto_direct_message.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # user_account = UserAccount.objects.get(id=data['user_id'])
        # context['user_accounts'] = UserAccount.objects.filter()
        return context

    def post(self, request, *args, **kwargs):
        dm_status = self.request.POST.get("togBtn", None)
        user_id = self.request.POST.get("insta_user_id", None)
        message = self.request.POST.get("Message", None)
        print(message, "aaaaaaaaaaaaaaaaaaaaaaaaaa")
        user_account = Chats.objects.get(id=user_id)
        user_account.autodirectmessage = True if dm_status == "True" else False
        user_account.directmessage = message
        user_account.save()
        return render(
            request,
            self.template_name,
            {"status": dm_status if dm_status == "True" else "False"},
        )


class AutoReplyCommentView(TemplateView):
    template_name = "dashboard/tools/telegram_auto_reply.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # user_account = UserAccount.objects.get(id=data['user_id'])
        # context['user_accounts'] = UserAccount.objects.filter()
        return context

    def post(self, request, *args, **kwargs):
        user_id = self.request.POST.get("insta_user_id", None)
        user_account = Chats.objects.get(id=user_id)
        user_account.autoreply = False if user_account.autoreply == True else True
        user_account.save()
        return render(request, self.template_name, {})


class ReplyCommentStatus(APIView):
    def get(self, request, *args, **kwargs):
        user_id = self.request.GET.get("insta_user_id", None)
        user_account = Chats.objects.get(id=user_id)
        return Response({"success": True, "status": user_account.autoreply})


class DirectMessageStatus(APIView):
    def get(self, request, *args, **kwargs):
        user_id = self.request.GET.get("insta_user_id", None)
        user_account = Chats.objects.get(id=user_id)
        return Response(
            {
                "success": True,
                "status": user_account.autodirectmessage,
                "message": user_account.directmessage,
            }
        )


class UserDirectMessageView(TemplateView):
    template_name = "dashboard/tools/telegram_user_direct_message.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # user_groups = SurviralGroup.objects.filter(user=user)
        # context["user_groups"] = user_groups
        return context

    def post(self, request, *args, **kwargs):
        cmnt = self.request.POST.get("your_cmnt", None)
        admin_id = self.request.POST.get("admin_user_id")
        user_account_id = self.request.POST.get("insta_user_id")
        timezone = self.request.POST.get("timezone")
        user = self.request.user
        scheduled_for = datetime.datetime.now(pytz.UTC)

        chats = Chats.objects.filter(id=user_account_id)
        chat_id = chats[0].chat_id if chats else None
        obj = TelegramUtilities(bot_api_key=TelegramBots.objects.get(bot_username='Madison2000_bot').bot_api_key)
        obj.post_message(message=cmnt, chat_id=chat_id)

        messages.success(request, "Your message sent on Telegram")
        return render(request, self.template_name, self.get_context_data())


class GroupDirectMessageView(TemplateView):
    template_name = "dashboard/tools/telegram_group_direct_message.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # user_groups = SurviralGroup.objects.filter(user=user)
        # context["user_groups"] = user_groups
        return context

    def post(self, request, *args, **kwargs):
        cmnt = self.request.POST.get("your_cmnt", None)
        admin_id = self.request.POST.get("admin_user_id")
        user_account_id = self.request.POST.get("insta_user_id")
        timezone = self.request.POST.get("timezone")
        user = self.request.user
        scheduled_for = datetime.datetime.now(pytz.UTC)

        chats = Chats.objects.filter(id=user_account_id)
        chat_id = chats[0].chat_id if chats else None
        obj = TelegramUtilities(bot_api_key=TelegramBots.objects.get(bot_username='Madison2000_bot').bot_api_key)
        obj.post_message(message=cmnt, chat_id=chat_id)

        messages.success(request, "Your message sent on Telegram")
        return render(request, self.template_name, self.get_context_data())
