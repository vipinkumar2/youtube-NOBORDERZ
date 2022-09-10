from django.contrib import admin
from twitterbot.models import *

class TwitterUserAdmin(admin.ModelAdmin):
	list_display = ('username', 'screen_name')
	
admin.site.register(TwitterAccount)
admin.site.register(TwitterJob)
admin.site.register(TwitterUser, TwitterUserAdmin)
admin.site.register(CompetitorUserDetials)
admin.site.register(TwitterActionLog)
admin.site.register(Tweet)