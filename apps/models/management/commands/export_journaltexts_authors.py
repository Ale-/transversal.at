# python
import sys, csv, os.path
# django
from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
from django.utils.encoding import smart_str
# project
from apps.models.models import JournalText

"""
A manage.py command to import JournalIssue objects from a CSV file
"""

class Command(BaseCommand):
    help = "Import Journal objects from a CSV file. Following columns are needed: \
            The only argument is a valid path to the CSV file."

    """
    Imports JournalIssue objects from a given CSV file
    """
    def handle(self, *args, **options):
        with open('journaltexts_authors.csv', 'w') as csv_file:
            fieldnames = ['title', 'slug', 'authors' ]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for obj in JournalText.objects.all():
                 writer.writerow({'title': smart_str(obj.title), 'slug': smart_str(obj.slug), 'authors' : [ i.fullname for i in obj.authors.all() ] })
