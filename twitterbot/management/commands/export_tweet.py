"""
 Prints CSV of all fields of a model.
"""

from django.core.management.base import BaseCommand, CommandError
import csv
import sys
from twitterbot.models import *


class Command(BaseCommand):
    help = "Output the specified model as CSV"
    args = "[appname.ModelName]"

    def handle(self, *app_labels, **options):
        model = Tweet
        field_names = [f.name for f in model._meta.fields]
        writer = csv.writer(sys.stdout, quoting=csv.QUOTE_ALL)
        writer.writerow(field_names)
        for instance in model.objects.all():
            writer.writerow([getattr(instance, f) for f in field_names])
