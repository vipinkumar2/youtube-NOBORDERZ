import base64
import jsonpickle
import pickle

from django.db import models
from datetime import datetime
# from oauth2_client import credentials_manager
from oauth2client import client
from django.utils import encoding
from django.db.models import JSONField
# Create your models here.

"""
FIELD FOR STORING GOOGLE OAUTH2 CREDENTIALS
"""


class CredentialsField(models.Field):
    """Django ORM field for storing OAuth2 Credentials."""

    def __init__(self, *args, **kwargs):
        if "null" not in kwargs:
            kwargs["null"] = True
        super(CredentialsField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "BinaryField"

    def from_db_value(self, value, expression, connection, context=None):
        """Overrides ``models.Field`` method. This converts the value
        returned from the database to an instance of this class.
        """
        return self.to_python(value)

    def to_python(self, value):
        """Overrides ``models.Field`` method. This is used to convert
        bytes (from serialization etc) to an instance of this class"""
        if value is None:
            return None
        elif isinstance(value, client.Credentials):
            return value
        else:
            try:
                return jsonpickle.decode(
                    base64.b64decode(encoding.smart_bytes(value)).decode()
                )
            except ValueError:
                return pickle.loads(base64.b64decode(encoding.smart_bytes(value)))

    def get_prep_value(self, value):
        """Overrides ``models.Field`` method. This is used to convert
        the value from an instances of this class to bytes that can be
        inserted into the database.
        """
        if value is None:
            return None
        else:
            return encoding.smart_text(
                base64.b64encode(jsonpickle.encode(value).encode())
            )

    def value_to_string(self, obj):
        """Convert the field value from the provided model to a string.

        Used during model serialization.

        Args:
            obj: db.Model, model object

        Returns:
            string, the serialized field value
        """
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)


class TimeStampModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

        
class YoutubeAccount_aws(TimeStampModel):
    email = models.EmailField(max_length=255, unique=True)
    token = models.CharField(max_length=1000, null=True, blank=True)
    credentials = CredentialsField()
    refresh_token = models.CharField(max_length=500, null=True, blank=True)
    expiry = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.email