# python
import sys, csv, os.path
# django
from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
# project
from apps.models.models import Biography, Book

"""
A manage.py command to import Book translators from a CSV file
"""

class Command(BaseCommand):
    help = "Import Book objects from a CSV file. Following columns are needed: \
            The only argument is a valid path to the CSV file."

    """
    Add CSV file as an argument to the parser
    """
    def add_arguments(self, parser):
        parser.add_argument('csv')

    """
    Import Book translators from a given CSV file
    """
    def handle(self, *args, **options):
        csv.field_size_limit(sys.maxsize)
        if not os.path.isfile(options['csv']):
             raise CommandError('The specified file does not exist. Have you written it properly?')
        with open(options['csv'], 'r') as f:
            rows = csv.DictReader(f)
            related_books = {}
            for row in rows:
                try:
                    book = Book.objects.get(title=row['title'])
                    translators_dids = []
                    if row['translators']:
                        translators_zids = [ id for id in row['translators'].split(",") ]
                        for translator_zid in translators_zids:
                            try:
                                p = Biography.objects.get(surname=translator_zid.strip())
                                translators_dids.append(p.pk)
                            except:
                                pass
                    book.translators.set(translators_dids)
                    book.save()
                except:
                    print("There was a problem with the book: %s" % row['title'])
