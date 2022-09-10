from django.contrib import admin
from django.urls import include, path

from core import views
from django.contrib.auth import views as auth_views

from django.contrib.auth.decorators import login_required

urlpatterns = [
    path("", views.LoginView.as_view(), name="user_login"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path(
        "verify_otp/", login_required(views.VerifyOTPView.as_view()), name="verify_otp"
    ),
    path("resend_email_otp/", views.ResendOTPView.as_view(), name="resend_email_otp"),
    path(
        "change_password/",
        login_required(views.ChangePasswordView.as_view()),
        name="change_password",
    ),
    path("account/", login_required(views.AccountView.as_view()), name="account"),
    path(
        "forgot_password/", views.ForgotPasswordView.as_view(), name="forgot_password"
    ),
    path("profile/", login_required(views.ProfileView.as_view()), name="profile"),
    path("package/", login_required(views.PackageView.as_view()), name="package"),
    path("logout/", views.logout, name="logout"),
]
