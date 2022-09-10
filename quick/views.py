import requests
import datetime
import random
import string
import json
import pytz
from django.contrib import messages
from django.contrib.auth import login
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth import logout as django_logout
from django.core.mail import send_mail, BadHeaderError, EmailMessage
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

# Create your views here.
from django.utils import translation
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
from dateutil.relativedelta import relativedelta
import logging
import constants
from core.models import User, EmailOTP
from instabot.models import UserAccount, Job
from membership.models import *
from membership import utils
import instaloader

URL = settings.INSTABOT_URL


def get_random_string(length=None):
    length = 8
    letters = string.ascii_lowercase
    result_str = "".join(random.choice(letters) for i in range(length))
    return result_str


def logout(request):
    django_logout(request)
    return redirect("/")


class EmailAuthBackend(object):
    """
    Email Authentication Backend

    Allows a user to sign in using an email/password pair rather than
    a username/password pair.
    """

    def authenticate(self, username=None, password=None):
        """ Authenticate a user based on email address as the user name. """
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except Exception as e:
            print("==================User does not exists==================")
            return None


# class UserLoginView(TemplateView):
#     template_name = "core/login.html"
#
#     def get(self, request):
#         if not request.user.is_authenticated:
#             return render(request, self.template_name, {})
#         else:
#             return redirect('/dashboard/')
#
#     def post(self, request):
#         username = request.POST.get('LoginForm[username]')
#         password = request.POST.get('LoginForm[password]')
#         user = EmailAuthBackend().authenticate(username=username, password=password)
#         if user:
#             login(request, user)
#             if UserAccount.objects.filter(user=user).exists():
#                 return redirect('/dashboard/')
#             else:
#                 return redirect('/dashboard/add_membership/')
#         else:
#             return render(request, self.template_name, {})
#
#
# class ForgotPasswordView(TemplateView):
#     template_name = "core/forgot_password.html"
#
#     def get(self, request):
#         if not request.user.is_authenticated:
#             return render(request, self.template_name, {})
#         else:
#             return redirect('/dashboard/')
#
#     def post(self,request):
#         email = request.POST.get('ForgotPasswordForm[email]')
#         try:
#             user = User.objects.get(email=email)
#             if user and user.is_active:
#                 subject = "Password Reset Requested"
#                 email_template_name = "password_reset/password_reset_email.txt"
#                 data = {
#                     "email":user.email,
#                     "domain":'127.0.0.1:8000',
#                     'site_name':'Website',
#                     "uid":urlsafe_base64_encode(force_bytes(user.pk)),
#                     "user":user,
#                     "token":default_token_generator.make_token(user),
#                     'protocol':'http'
#                 }
#                 email = render_to_string(email_template_name,data)
#                 try:
#                     send_mail(subject,email,user.email,[user.email],fail_silently=False)
#                 except BadHeaderError:
#                     return redirect('forgot-password')
#
#                 return render(request,'core/reset_password/password_recovery_mail_success.html')
#             else:
#                 return render(request,self.template_name,{})
#         except User.DoesNotExist:
#             return HttpResponse("User Does Not Exist")
#
# class ResetPasswordViews(TemplateView):
#     template_name = "core/reset_password/password_reset.html"
#
#     def get(self, request):
#         if not request.user.is_authenticated:
#             return render(request, self.template_name, {})
#         else:
#             return redirect('/dashboard/')
#
#     def dispatch(self, request, *args, **kwargs):
#         self.uidb64 = kwargs['uidb64']
#         self.token = kwargs['token']
#         assert 'uidb64' in kwargs and 'token' in kwargs
#         try:
#             uid = force_bytes(urlsafe_base64_decode(self.uidb64))
#             user = User.objects.get(pk=uid)
#         except (TypeError,ValueError,OverflowError,User.DoesNotExist):
#             user = None
#         if request.user.is_authenticated:
#              return redirect('/dashboard/')
#
#         if user is not None and default_token_generator.check_token(user,self.token):
#             # user.is_active = True
#             if request.method == "POST":
#                 password1 = request.POST.get('ResetPasswordForm[password]')
#                 password2 = request.POST.get('ResetPasswordForm[password_repeat]')
#                 if password1 == password2:
#                     user.set_password(password1)
#                     user.save()
#                     return render(request,'core/reset_password/password_reset_done.html')
#                 else:
#                     return render(request,'core/reset_password/password_reset.html',{'token':self.token,'uidb64':self.uidb64})
#             else:
#                 return render(request,'core/reset_password/password_reset.html',{'token':self.token,'uidb64':self.uidb64})
#         else:
#             return render(request,'core/reset_password/wrong_reset_password_token.html')
#
# class SignUpView(TemplateView):
#     template_name = "core/signup.html"
#
#
#     def get(self, request):
#         if not request.user.is_authenticated:
#             return render(request, self.template_name, {})
#         else:
#             return redirect('/dashboard/add_membership/')
#
#     def post(self, request):
#         email = request.POST.get('SignupForm[email]')
#         password = request.POST.get('SignupForm[password]')
#         confirm_password = request.POST.get('SignupForm[password_repeat]')
#         if email and password and confirm_password and (password == confirm_password):
#             try:
#                 user = User.objects.create_user(email=email, password=password)
#                 if user:
#                     login(request, user)
#                     # request.session['username'] = user.username
#                     return redirect('/dashboard/add_membership/')
#             except Exception as e:
#                 print(f"============Error while sign up is: str(e)=========================")
#                 return render(request, self.template_name, {})
#         else:
#             return render(request, self.template_name, {})


class LoginView(TemplateView):
    template_name = "core/viral_ignitor_user/quick_login.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not UserAccount.objects.filter(user=request.user).exists():
                return redirect("multistep_form")
            return redirect("edit_user_details")

        else:
            return render(request, self.template_name, {})

    def post(self, request):
        username = request.POST.get("email")
        password = request.POST.get("password")
        language = request.POST.get("language")
        user = EmailAuthBackend().authenticate(username=username, password=password)
        if user:
            login(request, user)
            translation.activate(self.request.user.user_language)
            if not UserAccount.objects.filter(user=user).exists():
                return redirect("multistep_form")
            messages.success(request, constants.LOGIN_SUCCESS_MESSAGE)
            return redirect("edit_user_details")
        else:
            messages.error(request, constants.INVALID_USERNAME_PASSWORD_MESSAGE)
            return render(request, self.template_name, {})


# class SendEmailOTPView(TemplateView):
#     template_name = "core/viral_ignitor_user/signup.html"


class SendEmailOTPView(View):
    def send_otp_on_email(self, to_emails, email_body):
        """
        Create sendgrid Mail object
        """

        # mail = EmailMessage("Verification OTP", email_body, "support@surviral.io", [to_emails,])
        # mail.content_subtype = "html"
        # response = mail.send()
        # logging.info(f"Email sent from aws status {response}")

        # return response

        message = Mail(
            from_email="support@surviral.io",
            to_emails=[
                to_emails,
            ],
            subject="Surviral: Email Verification",
            html_content=email_body,
        )

        # """
        #     Send otp on email
        # """

        try:
            sendgrid_client = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sendgrid_client.send(message)
            return response
        except Exception as e:
            logging.info(
                "======================================================================"
            )
            logging.info(e)
            logging.info(
                "======================================================================"
            )
            return False

    def get(self, request, *args, **kwargs):
        email = request.GET.get("email", None)
        status = False
        if not User.objects.filter(email=email):
            verification_code = random.randint(100000, 999999)
            email_body = "Your Surviral Verification Code is : " + str(
                verification_code
            )
            response = self.send_otp_on_email(to_emails=email, email_body=email_body)

            if response:
                email_otps = EmailOTP.objects.filter(email=email)
                if email_otps:
                    email_otps.update(generated_otp=verification_code)
                else:
                    EmailOTP.objects.create(
                        email=email, generated_otp=verification_code
                    )
            status = True

        return JsonResponse({"status": status})


class SignUpView(TemplateView):
    template_name = "core/viral_ignitor_user/signup.html"

    def send_otp_on_email(self, from_email, to_emails, email_subject, html_content):

        message = Mail(
            from_email=from_email,
            to_emails=to_emails,
            subject=email_subject,
            html_content=html_content,
        )

        try:
            sendgrid_client = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sendgrid_client.send(message)
            return response
        except Exception as e:
            logging.info(
                "======================================================================"
            )
            logging.info(e)
            logging.info(
                "======================================================================"
            )
            return False

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, self.template_name, {})
        else:
            return redirect("/dashboard/")

    def post(self, request, *args, **kwargs):
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        timezone = request.POST.get("timezone")
        language = request.POST.get("language")
        if email and password and confirm_password and timezone:
            if password == confirm_password:
                try:
                    user = User.objects.create_user(
                        email=email,
                        password=password,
                        timezone=timezone,
                        user_language=language,
                    )
                    verification_code = random.randint(100000, 999999)
                    email_body = "Your Surviral Verification Code is : " + str(
                        verification_code
                    )
                    response = self.send_otp_on_email(
                        "office@noborders.net", email, "Verification OTP", email_body
                    )
                    print(email_body, " email body")
                    EmailOTP.objects.create(user=user, generated_otp=verification_code)
                    if user:
                        login(request, user)
                        plan = Plan.objects.get(name__iexact="early")
                        Subscription.objects.create(plan=plan, user=request.user)
                        messages.success(request, constants.USER_CREATED_MESSAGE)
                        return redirect("add_instagram_account")

                except Exception as e:
                    print(e)
                    if "Key (email)" in str(e):
                        messages.warning(request, constants.EMAIL_ALREADY_EXISTS)
                    else:
                        messages.warning(request, constants.ERROR_CREATING_USER)
                    return render(request, self.template_name, {})
            else:
                messages.warning(request, constants.PASSWORD_MISMATCHED)
                return render(request, self.template_name, {})
        else:
            messages.error(request, constants.INVALID_SIGNUP_INPUTS)
            return render(request, self.template_name, {})


# class VerifyOTPView(TemplateView):
#     template_name = "dashboard/viral_ignitor/dashboard.html"
#
#     def post(self, request, *args, **kwargs):
#         try:
#             received_otp = self.request.POST.get('verify_otp')
#             generated_otp = EmailOTP.objects.get(user=self.request.user).generated_otp
#             if received_otp == generated_otp:
#                 user = User.objects.get(id=self.request.user.id)
#                 user.email_verified = True
#                 user.save()
#                 return render(request, self.template_name, {})
#             else:
#                 return render(request, self.template_name, {})
#         except Exception as e:
#             logging.info(e)
#             return render(request, self.template_name, {})


class VerifyOTPView(View):
    def get(self, request, *args, **kwargs):
        received_otp = self.request.GET.get("otp")
        email = self.request.GET.get("email")
        status = False
        if email and received_otp:
            if EmailOTP.objects.filter(email=email, generated_otp=received_otp):
                status = True
        return JsonResponse({"status": status})


class ChangePasswordView(TemplateView):
    template_name = "core/viral_ignitor_user/change_password.html"

    def post(self, request, *args, **kwargs):
        current_password = request.POST.get("current_password")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        user = EmailAuthBackend().authenticate(
            username=self.request.user.username, password=current_password
        )
        if user:
            if password == confirm_password:
                user.set_password(password)
                user.save()
                messages.success(request, constants.PASSWORD_CHANGES)
            else:
                messages.warning(request, constants.PASSWORD_CONFIRM_PASSWORD_ERROR)
        else:
            messages.error(request, constants.INCORRECT_PASSWORD)
        return render(request, self.template_name, {})


class ForgotPasswordView(TemplateView):
    template_name = "core/viral_ignitor_user/forgot_password.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, self.template_name, {})
        else:
            return redirect("/dashboard/")

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            if user and user.is_active:
                subject = "Surviral: Password Reset Requested"
                email_template_name = "password_reset/password_reset_email.txt"
                password = get_random_string()
                data = {
                    "email": user.email,
                    "site_name": "Surviral Web",
                    "password": password,
                    "user": user,
                }
                email_body = render_to_string(email_template_name, data)
                try:
                    send_mail(
                        subject,
                        email_body,
                        "support@surviral.io",
                        [user.email],
                        fail_silently=False,
                    )
                    messages.success(request, constants.EMAIL_SEND_MESSAGE)
                except BadHeaderError:
                    messages.error(request, constants.EMAIL_SEND_ERROR_MESSAGE)
                    return redirect("/forgot_password/")
                user.set_password(password)
                user.save()
                return redirect("/quick/")
            else:
                messages.warning(request, constants.ACCOUNT_INACTIVE)
                return render(request, self.template_name, {})
        except User.DoesNotExist:
            messages.error(request, constants.INVALID_EMAIL)
            return render(request, self.template_name, {})


class ProfileView(TemplateView):
    template_name = "core/viral_ignitor_user/profile.html"


class PackageView(TemplateView):
    template_name = "core/viral_ignitor_user/package.html"


class AccountView(TemplateView):
    template_name = "core/viral_ignitor_user/account.html"

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        timezone = request.POST.get("timezone")
        language = request.POST.get("language")

        if email and timezone:
            try:
                User.objects.filter(username=self.request.user.username).update(
                    email=email, timezone=timezone, user_language=language
                )

                messages.success(request, constants.UPDATED_SUCCESSFULLY)
                return redirect("/account/")
            except:
                messages.error(request, constants.ERROR_UPDATING)
                return redirect("/account/")

        else:
            messages.error(request, constants.MISSING_UPDATE_FIELDS)
            return redirect("/account/")


class MultiStepFormView(TemplateView):
    template_name = "core/viral_ignitor_user/multistep-form.html"

    def send_otp_on_email(self, to_emails, email_body):
        """
        Create sendgrid Mail object
        """

        message = Mail(
            from_email="office@noborders.net",
            to_emails=to_emails,
            subject="Verification OTP",
            html_content=email_body,
        )

        """
            Send otp on email
        """

        try:
            sendgrid_client = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sendgrid_client.send(message)
            return response
        except Exception as e:
            logging.info(
                "======================================================================"
            )
            logging.info(e)
            logging.info(
                "======================================================================"
            )
            return False

    def post(self, request):
        data = self.request.POST
        """
        Personal Details
        """
        username = data.get("user_name")
        email = data.get("user_email")
        user_password = data.get("user_password")
        user_cpassword = data.get("user_cpassword")
        """
        Instagram Account Details
        """
        insta_account = data.get("insta_account")
        insta_password = data.get("insta_password")
        insta_account_about = data.get("insta_account_about")
        """
        User Target
        """
        target_audience = data.get("target_audience")
        target_area = data.get("target_area")
        target_gender = data.get("target_gender")
        target_compititor = data.get("target_compititor")

        if User.objects.filter(username=username, email=email).exists():
            return render(
                request,
                self.template_name,
                {
                    "message": "User already exist with username or email",
                    "data": dict(data),
                    "error": True,
                },
            )

        if (
            user_password != user_cpassword
            or User.objects.filter(username=username, email=email).exists()
        ):
            return render(
                request,
                self.template_name,
                {
                    "message": "Password and Confirm password not matched",
                    "data": dict(data),
                    "error": True,
                },
            )

        try:
            """
            Create User Account
            """
            user = User.objects.create(
                email=email,
                username=username,
            )
            user.set_password(user_password)
            user.save()

            """
            Generate and Send OTP on user's email for email verification
            """

            verification_code = random.randint(100000, 999999)
            email_body = "Your Surviral Verification Code is : " + str(
                verification_code
            )
            response = self.send_otp_on_email(to_emails=email, email_body=email_body)
            if response:
                EmailOTP.objects.create(user=user, generated_otp=verification_code)
        except Exception as e:
            print(e)
            return render(
                request,
                self.template_name,
                {"message": "Unable to create User account.", "data": dict(data)},
            )
        try:
            """
            1. Add given instagram Account
            2. Add targeting details
            3. Create Get Profile job
            """
            user_account = UserAccount.objects.create(
                user=user,
                account_type="IG",
                account_username=insta_account,
                account_password=insta_password,
                status="A",
                data={"account_data": insta_account_about},
                target_auidience=target_audience,
                competitors=target_compititor,
                target_area=target_area,
                target_gender=target_gender,
            )

            job = Job.objects.create(
                user=user_account.user,
                user_account=user_account,
                job_type="LOGIN_USER",
                job_title="""Get User's Profile""",
                app_type="IG",
                scheduled_for=datetime.datetime.now(pytz.utc),
                status="P",
            )
        except:
            User.objects.filter(pk=user.id).delete()
            return render(
                request,
                self.template_name,
                {
                    "message": "Unable to add instagram account, someone already added.",
                    "data": dict(data),
                    "error": True,
                },
            )

        """
        Login new user and assign early plan for 2 day free access.
        """

        login(request, user)
        plan = Plan.objects.get(name__iexact="early")
        Subscription.objects.create(plan=plan, user=request.user)
        return redirect("edit_user_details")
        # return render(request,
        #               'dashboard/viral_ignitor/dashboard.html', {})

    def get(self, request, *args, **kwargs):
        countries = constants.COUNTRIES
        if not request.user.is_authenticated:
            return render(request, self.template_name, {"countries": countries})
        elif not UserAccount.objects.filter(user=request.user).exists():
            return render(request, self.template_name, {"countries": countries})
        else:
            return redirect("edit_user_details")


class EditUserDetailsView(TemplateView):
    template_name = "core/viral_ignitor_user/edit_user_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["countries"] = constants.COUNTRIES
        context["about_categories"] = constants.ABOUT_CATEGORY
        return context

    def get(self, request):
        context = self.get_context_data()
        user = self.request.user
        user_account = UserAccount.objects.filter(user=user).first()
        if not user_account:
            return redirect("multistep_form")
        subscription = Subscription.objects.filter(
            user=self.request.user, is_active=True
        ).order_by("-created")
        if subscription.exists() and subscription.last().plan.plan_type == "month":
            subscription = subscription.last()
            created = subscription.created
            expire = created + relativedelta(months=1)
        elif subscription.exists() and subscription.last().plan.plan_type == "year":
            subscription = subscription.last()
            created = subscription.created
            expire = created + relativedelta(years=1)
        else:
            created = user.created
            expire = created + datetime.timedelta(days=2)

        if expire.date() <= datetime.datetime.now().date():
            return redirect("quick_pricing")

        return render(request, self.template_name, context)

    def post(self, request):
        context = self.get_context_data()
        data = request.POST
        useraccount_id = data.get("user_id")
        # insta_account = data.get('insta_account')
        # insta_password = data.get('insta_password')
        insta_account_about = data.get("account_about")
        country = data.get("select_country")
        language = data.get("language")
        timezone = data.get("timezone")
        target_competitor = ",".join(data.getlist("yourCompetitors"))
        target_competitor = target_competitor.replace(" ", "")
        user = request.user
        user.user_language = language
        user.timezone = timezone
        user.save()
        translation.activate(language)
        user_account_qs = user.useraccount_set.filter(id=useraccount_id)
        if user_account_qs.exists():
            user_account = user_account_qs.first()
            # user_account.account_username = insta_account
            # user_account.account_password = insta_password
            user_account.country = country
            user_account.data["account_data"] = insta_account_about
            user_account.competitors = target_competitor
            user_account.save()
            context["message"] = constants.ACCOUNT_INFO_UPDATE

        return render(request, self.template_name, context)


class ValidationView(View):
    def get(self, request, *args, **kwargs):
        username = request.GET.get("username", None)
        email = request.GET.get("email", None)
        instaAccount = request.GET.get("account", None)
        valid = False
        if email:
            obj = User.objects.filter(email=email).exists()
            if obj:
                valid = True
            else:
                try:
                    obj = validate_email(email)
                    valid = False
                except:
                    valid = True
        elif username:
            valid = User.objects.filter(username=username).exists()

        elif instaAccount:
            valid = UserAccount.objects.filter(account_username=instaAccount).exists()

        return JsonResponse({"status": valid})


class SignupApi(View):
    def post(self, request):
        data = self.request.POST
        """
        Personal Details
        """
        username = data.get("username")
        email = data.get("email")
        timezone = data.get("timezone")
        password = data.get("password")
        cpassword = data.get("cpassword")
        language = data.get("language")
        if len(password) < 8:
            return JsonResponse(
                {
                    "status": False,
                    "message": "Please enter minimum 8 character password ",
                }
            )
        if User.objects.filter(username=username, email=email).exists():
            return JsonResponse(
                {"status": False, "message": "User alredy exists with username."}
            )
        if (
            password != cpassword
            or User.objects.filter(username=username, email=email).exists()
        ):
            return JsonResponse(
                {"status": False, "message": "Confirm password did not matched."}
            )

        try:
            """
            Create User Account
            """
            user = User.objects.create(
                email=email,
                username=username,
                timezone=timezone,
                user_language=language,
                email_verified=True,
            )

            user.set_password(password)
            user.save()
            login(request, user)
        except Exception as e:
            print(e)
            return JsonResponse({"status": False, "message": "Something went wrong"})

        return JsonResponse(
            {
                "status": True,
                "message": "Account Created successfully",
                "user_id": user.id,
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class AddInstagramAccount(View):
    def post(self, request):
        data = self.request.POST
        """
        Instagram Details
        """
        user_id = data.get("user_id")
        insta_account = data.get("insta_account")
        insta_password = data.get("insta_password")
        insta_account_about = data.get("insta_account_about")
        insta_country = data.get("insta_country")

        user_qs = User.objects.filter(id=user_id)
        try:
            if user_qs.exists():
                url = URL + "account_check/"
                data = {"account": insta_account, "password": insta_password}
                print(
                    f"====================URL used:- {str(url)}================================"
                )
                print(
                    f"====================Data Passed:- {str(data)}================================"
                )
                response = requests.post(url=url, data=data)

                if response.status_code == 200:
                    if response.json()["status"]:
                        """
                        Saving instagram account details
                        """
                        user_account = UserAccount.objects.create(
                            user=user_qs.first(),
                            account_type="IG",
                            account_username=insta_account,
                            account_password=insta_password,
                            status="A",
                            country=insta_country,
                            data={"account_data": insta_account_about},
                        )

                        """
                        creating job to get profile details
                        """
                        Job.objects.create(
                            user=user_account.user,
                            user_account=user_account,
                            job_type="GET_PROFILE",
                            job_title="""Get User's Profile""",
                            app_type="IG",
                            scheduled_for=datetime.datetime.now(pytz.timezone("UTC")),
                            timezone="UTC",
                            status="P",
                        )
                    else:
                        return JsonResponse(
                            {
                                "status": False,
                                "message": "Unable to login with provided credentials, Please try again.",
                            }
                        )
                else:

                    return JsonResponse(
                        {
                            "status": False,
                            "message": "Something wrong in instagram bot check_account api",
                        }
                    )
            else:
                return JsonResponse(
                    {
                        "status": False,
                        "message": "Unable to find user, Please try again.",
                    }
                )

        except Exception as e:
            print(e)
            return JsonResponse(
                {"status": False, "message": "Unable to create instagram account"}
            )

        return JsonResponse(
            {
                "status": True,
                "user_id": user_qs.first().id,
                "useraccount_id": user_account.id,
                "message": "Instagram account added successfully.",
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class AddUserTarget(View):
    def post(self, request):
        data = self.request.POST
        """
        Instagram Details
        """
        useraccount_id = data.get("useraccount_id")
        targetAudience = data.get("targetAudience", None)
        targetArea = data.get("targetArea", None)
        targetGender = data.get("targetGender", None)
        yourCompetitors = ",".join(data.getlist("yourCompetitors[]"))
        yourCompetitors = yourCompetitors.replace(" ", "")
        if useraccount_id:
            useraccount_qs = UserAccount.objects.filter(id=useraccount_id)
        else:
            return JsonResponse({"status": False})

        try:
            if useraccount_qs.exists():
                UserAccount.objects.filter(id=useraccount_id).update(
                    competitors=yourCompetitors,
                )
            else:
                return JsonResponse(
                    {
                        "status": False,
                        "message": "Unable to find instagram account, Please try again.",
                    }
                )

        except:
            return JsonResponse(
                {"status": False, "message": "Unable to create instagram account"}
            )

        return JsonResponse(
            {
                "status": True,
                "useraccount_id": useraccount_qs.first().id,
                "message": "Instagram account added successfully.",
            }
        )


class PricingView(TemplateView):
    template_name = "dashboard/viral_ignitor/quick_pricing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plans = Plan.objects.filter(is_active=True, plan_type="month")
        yearly_plans = Plan.objects.filter(is_active=True, plan_type="year")

        context["plans"] = plans
        context["yearly_plans"] = yearly_plans
        return context


class PaymentView(TemplateView):
    template_name = "dashboard/viral_ignitor/quick_payment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stripe_plan_id = self.kwargs.get("plan_id")
        plans = Plan.objects.filter(stripe_plan_id=stripe_plan_id)
        if plans:
            context["plan"] = plans.first()
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        name = request.POST["name"]
        line1 = request.POST["line1"]
        country = request.POST["country"]
        if not hasattr(request.user, "stripe_user"):
            utils.create_stripe_customer(request.user, line1, country)
        stripe_user = request.user.stripe_user

        card_id = request.POST.get("card_id", None)
        try:
            stripe_customer_card = None
            if card_id == "other_card":
                card_number = request.POST["card_number"]
                expiry = request.POST["expiry"]
                expiry_month = int(expiry.split("/")[0])
                expiry_year = int(expiry.split("/")[1])
                cvv = request.POST["cvv"]

                source = utils.create_card_token(
                    card_number, expiry_month, expiry_year, cvv
                )
                stripe_customer_card = utils.assign_source_to_customer(
                    stripe_user, source
                )
            else:
                stripe_customer_card = card_id
            subscription_id = utils.subscribe_stripe_user(
                context["plan"], stripe_user, request.user
            )
            utils.save_payment_history(
                request.user, context["plan"].amount, subscription_id
            )
            context["subscription_id"] = subscription_id

        except Exception as ex:
            logging.exception(ex)
            context["message"] = "Subscription Failed. Please try again"

            context["card_number"] = card_number
            context["expiry"] = expiry
            context["cvv"] = cvv
            if stripe_customer_card:
                utils.remove_customer_cards(
                    stripe_user.stripe_customer_id, stripe_customer_card
                )
            context["name"] = name
            context["line1"] = line1
            context["country"] = country
        return render(request, self.template_name, context)


from django.views.generic import TemplateView, CreateView


class InsertOTPQuickView(CreateView):
    def post(self, request, *args, **kwargs):
        print(self.request.POST)
        otp = self.request.POST.get("user_id", None)
        if not otp:
            otp = self.request.POST.get("user_id_otp", None)
        user_account = UserAccount.objects.get(id=otp)
        if "otp" in self.request.POST:
            otp = self.request.POST.get("otp")
            user_account.data["otp"] = otp
            user_account.login_status = "P"
            user_account.save()
            messages.success(request, "Got OTP!")
        else:
            messages.error(request, constants.OTP_REQUIRED_MESSAGE)
        return redirect("edit_user_details")


class TermsViews(TemplateView):
    template_name = "dashboard/viral_ignitor/terms.html"


class PrivacyPolicyView(TemplateView):
    template_name = "dashboard/viral_ignitor/policy.html"
