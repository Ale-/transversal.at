# python
import sys, csv, os.path
# django
from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
from django.conf import settings
# project
from apps.models.models import Book, Image

"""
A manage.py command to import JournalIssue objects from a CSV file
"""

class Command(BaseCommand):
    help = "Import Journal objects from a CSV file. Following columns are needed: \
            The only argument is a valid path to the CSV file."

    """
    Add CSV file as an argument to the parser
    """
    def add_arguments(self, parser):
        parser.add_argument('--delete', default=False, help='Delete current objects')

    """
    Imports JournalIssue objects from a given CSV file
    """
    def handle(self, *args, **options):
        if options['delete']:
            Image.objects.all().delete()
        books = Book.objects.all()
        for book in books:
            image = Image(
                image_file = '/img/books/' + book.slug + '.png',
                source_content = book
            )
            image.save()
            book.pdf_file = '/pdf/' + book.slug + '.pdf'
            book.epub_file = '/epub/' + book.slug + '.epub'
            book.save()
