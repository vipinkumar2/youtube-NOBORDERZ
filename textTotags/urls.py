from django.urls import include, path
from .views import *

urlpatterns = [
    path("keyword_to_hastag/", KeywordToTags.as_view(), name="keyword_to_hastag"),
    path("caption_to_hastag/", CaptionToTags.as_view(), name="caption_to_hastag"),
]
