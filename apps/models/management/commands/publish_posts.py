# python
import sys, os.path
# django
from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
# project
from apps.models.models import BlogTextTranslation

"""
A manage.py command to import Book translators from a CSV file
"""

class Command(BaseCommand):
    help = "Import Book objects from a CSV file. Following columns are needed: \
            The only argument is a valid path to the CSV file."

    """
    Import Book translators from a given CSV file
    """
    def handle(self, *args, **options):
        posts = BlogTextTranslation.objects.all().update(is_published = True)
