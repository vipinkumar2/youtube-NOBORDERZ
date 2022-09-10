from django.db import models

# Create your models here.
from core.models import User


class TimeStampModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TelegramAccounts(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_username = models.CharField(max_length=50, null=True, blank=True)


class TelegramBots(TimeStampModel):
    telegram_Account = models.ForeignKey(TelegramAccounts, on_delete=models.CASCADE)
    chats = models.ManyToManyField('Chats', related_name='telegrambots')
    bot_username = models.CharField(max_length=50, null=True, blank=True)
    bot_api_key = models.CharField(max_length=100, null=True, blank=True)


class Chats(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True)
    chat_id = models.CharField(max_length=50, null=True, blank=True)
    type = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    autodirectmessage = models.BooleanField(default=False)
    directmessage = models.TextField(null=True, blank=True)
    autoreply = models.BooleanField(default=False)


class QuestionAnswer(TimeStampModel):
    question = models.CharField(max_length=500, null=True, blank=True)
    status = models.BooleanField(default=False)


class QNA(TimeStampModel):
    question = models.CharField(max_length=500, null=True, blank=True)
    answers = models.JSONField(null=True, blank=True)