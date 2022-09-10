"""surviral_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    # path('quick/', include('textTotags.urls')),
    url("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    path("advance/", include("core.urls")),
    path("advance/dashboard/", include("dashboard.urls")),
    path("advance/twitter/", include("twitterbot.urls")),
    path("advance/telegram_bot/", include("telegram_bot.urls")),
    path("advance/", include("django.contrib.auth.urls")),
    path("quick/", include("quick.urls")),
    
)
