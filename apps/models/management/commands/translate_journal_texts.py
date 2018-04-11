# python
import sys, csv, os.path
# django
from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
from django.utils.text import slugify
# project
from apps.models import models

"""
A manage.py command to update metadata
"""

class Command(BaseCommand):
    help = "Import Journal objects from a CSV file. Following columns are needed: \
            The only argument is a valid path to the CSV file."

    """
    Associate journal texts with its translations
    """
    def handle(self, *args, **options):
        journal_texts = models.JournalText.objects.all()
        for t in journal_texts:
            authors = [ a.pk for a in t.authors.all() ]
            texts  = models.JournalText.objects.filter(issue=t.issue, authors__in=authors).exclude(pk=t.pk)
            t.translations.set(texts)
            t.save()
