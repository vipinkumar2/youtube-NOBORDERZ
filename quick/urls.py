from django.contrib import admin
from django.urls import include, path

from quick import views
from quick import api_views
from django.contrib.auth import views as auth_views

from django.contrib.auth.decorators import login_required

urlpatterns = [
    path("", views.LoginView.as_view(), name="user_login_quick"),
    path("verify_otp/", views.VerifyOTPView.as_view(), name="verify_otp_quick"),
    path(
        "forgot_password/", views.ForgotPasswordView.as_view(), name="forgot_password"
    ),
    path("logout/", views.logout, name="logout"),
    path("multistep_form/", views.MultiStepFormView.as_view(), name="multistep_form"),
    path(
        "edit_user_details/",
        login_required(views.EditUserDetailsView.as_view()),
        name="edit_user_details",
    ),
    path(
        "valid_email_user_account/",
        views.ValidationView.as_view(),
        name="valid_email_user_account",
    ),
    path("create_user/", views.SignupApi.as_view(), name="create_user"),
    path(
        "add_instagram_account/",
        views.AddInstagramAccount.as_view(),
        name="add_instagram_account_quick",
    ),
    path("add_user_target/", views.AddUserTarget.as_view(), name="add_user_target"),
    path(
        "send_verification_email/",
        views.SendEmailOTPView.as_view(),
        name="send_verification_email",
    ),
    path(
        "search_insta_user/",
        api_views.SearchInstagramUserAccount.as_view(),
        name="search_insta_user",
    ),
    path("pricing/", login_required(views.PricingView.as_view()), name="quick_pricing"),
    path(
        "payment/<str:plan_id>/",
        login_required(views.PaymentView.as_view()),
        name="quick_payment",
    ),
    path(
        "quick_insert_otp/",
        login_required(views.InsertOTPQuickView.as_view()),
        name="quick_insert_otp",
    ),
    path(
        "check_quick_login_status/",
        login_required(api_views.CheckQuickLoginStatus.as_view()),
        name="check_quick_login_status",
    ),
    path("decode_string/", api_views.GetDecodedString.as_view(), name="decode_string"),
    path("terms/", views.TermsViews.as_view(), name="terms"),
    path("privacy-policy/", views.PrivacyPolicyView.as_view(), name="privacy-policy"),
]
