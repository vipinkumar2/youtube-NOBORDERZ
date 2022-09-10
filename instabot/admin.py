from django.contrib import admin
from .models import (
    Job,
    UserAccount,
    AccountAnalytics,
    Device,
    JobQueue,
    SurviralGroup,
    InstaAccFollowingsFollowers,
    UnfollowUsername,
    UserGoogleAccount,
    GoogleJobs,
    Phone,
    DailyAccountData,
)


admin.site.register(Job)

admin.site.register(UserAccount)
admin.site.register(AccountAnalytics)
admin.site.register(Device)
admin.site.register(JobQueue)
admin.site.register(SurviralGroup)
admin.site.register(UnfollowUsername)
admin.site.register(InstaAccFollowingsFollowers)
admin.site.register(UserGoogleAccount)
admin.site.register(GoogleJobs)
admin.site.register(Phone)
admin.site.register(DailyAccountData)
