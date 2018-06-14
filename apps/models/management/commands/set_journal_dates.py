# python
import os
# django
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
# project
from apps.models.models import JournalText

"""
A manage.py command to import all objects into database
"""

class Command(BaseCommand):
    help = "Import Biography objects from a CSV file. Following columns are needed: \
            The only argument is a valid path to the CSV file."

    """
    Imports Initiative models from a given CSV file
    """
    def handle(self, *args, **options):
        texts = JournalText.objects.all()
        for text in texts:
            if not text.date:
                text.date = text.issue.date
                text.save()
