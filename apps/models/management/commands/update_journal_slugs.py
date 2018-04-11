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

    def update_metadata(self, item):
        metadata = item.metadata.first()
        for field in ['effective_date', 'expiration_date', 'content_author', 'content_contributors', 'copyright', 'comments', 'is_published']:
            setattr(item, field, getattr(metadata, field))
        item.save()

    """
    Imports JournalIssue objects from a given CSV file
    """
    def handle(self, *args, **options):
        journal_texts = models.JournalText.objects.all()
        for t in journal_texts:
            # slug = ""
            # if t.authors:
            #     for author in t.authors.all():
            #         if author.surname:
            #             slug += slugify(author.surname)
            #         else:
            #             slug += slugify(author.name)
            # else:
            #     slug = slugify(t.title)
            # t.slug = slug
            t.save()
