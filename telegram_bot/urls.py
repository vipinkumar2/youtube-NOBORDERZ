from django.urls import path
from django.conf.urls import include
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from telegram_bot import views
urlpatterns = [
    path(
        "group-direct-message/",
        views.GroupDirectMessageView.as_view(),
        name="group-direct-message",
    ),

    path(
        "auto-direct-message/",
        views.UserDirectMessageView.as_view(),
        name="auto-direct-message",
    ),

    path(
        "auto_direct_message/",
        views.AutoDirectMessageView.as_view(),
        name="auto-direct-message",
    ),

    path(
        "auto_reply/",
        login_required(views.AutoReplyCommentView.as_view()),
        name="auto-reply",
    ),
    path(
        "reply_comment_status/",
        login_required(views.ReplyCommentStatus.as_view()),
        name="reply-comment-status",
    ),
    path(
        "telegram_direct_message_status/",
        login_required(views.DirectMessageStatus.as_view()),
        name="telegram_direct_message_status",
    ),
]