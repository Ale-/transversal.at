# python
import sys, csv, os.path, urllib.request
# django
from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
from django.utils.encoding import smart_str
# project
from apps.models.models import Book, Metadata

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
        books = Book.objects.all()
        for book in books:
            if book.metadata.first().is_published:
                print(book.title)
                filename = "/var/www/transversal.at/public_html/media/img/books/" + book.slug + ".png"
                if not os.path.isfile(filename):
                    url = 'http://transversal.at/books/'+book.slug+'/coverimg'
                    urllib.request.urlretrieve(url, filename)
