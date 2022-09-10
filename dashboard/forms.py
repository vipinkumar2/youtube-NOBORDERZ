from django import forms
from instabot.models import UserAccount
import constants


class AddInstagramAccountForm(forms.ModelForm):
    class Meta:
        model = UserAccount
        fields = ["user", "account_username", "account_password", "country"]
