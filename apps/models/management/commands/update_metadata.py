# python
import sys, csv, os.path
# django
from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
# project
from apps.models import models

"""
A manage.py command to update metadata
"""

class Command(BaseCommand):
    help = "Import Journal objects from a CSV file. Following columns are needed: \
            The only argument is a valid path to the CSV file."

    def update_metadata(self, item):
        metadata = item.metadata.first()
        for field in ['effective_date', 'expiration_date', 'content_author', 'content_contributors', 'copyright', 'comments', 'is_published']:
            setattr(item, field, getattr(metadata, field))
        item.save()

    """
    Imports JournalIssue objects from a given CSV file
    """
    def handle(self, *args, **options):
        classes = [ models.Biography ]
        for c in classes:
            items = c.objects.all()
            for i in items:
                self.update_metadata(i)
