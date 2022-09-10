from django.urls import path
from twitterbot import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

urlpatterns = [
	path(
		"follow/", 
		login_required(views.FollowAPIView.as_view()), 
		name="follow"
	),
	path(
		"multiple-follow/", 
		login_required(views.MultipleFollowAPIView.as_view()), 
		name="multiple-follow"
	),
	path(
		"tweet/", 
		login_required(views.TweetView.as_view()), 
		name="tweet"
	),
	path(
		"retweet/", 
		login_required(views.RetweetAPIView.as_view()), 
		name="retweet"
	),
	path(
		"like-on-tweet/", 
		login_required(views.LikeOnTweetAPIView.as_view()), 
		name="like-on-tweet"
	),
]