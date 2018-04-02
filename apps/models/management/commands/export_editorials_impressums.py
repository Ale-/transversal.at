# python
import sys, csv, os.path
# django
from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
from django.utils.encoding import smart_str
# project
from apps.models.models import JournalIssue

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
        with open('editorials_impressums.csv', 'w') as csv_file:
            fieldnames = ['title', 'editorial', 'impressum']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for obj in JournalIssue.objects.all():
                 writer.writerow({'title': obj.title, 'editorial': obj.editorial.strip(), 'impressum' : obj.impressum.strip() })
