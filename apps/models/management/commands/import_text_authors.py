# python
import sys, csv, os.path
from ast import literal_eval
# django
from django.core.management.base import BaseCommand, CommandError
# project
from apps.models.models import JournalText, Biography

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
        parser.add_argument('csv')

    """
    Imports JournalIssue objects from a given CSV file
    """
    def handle(self, *args, **options):
        csv.field_size_limit(sys.maxsize)
        if not os.path.isfile(options['csv']):
             raise CommandError('The specified file does not exist. Have you written it properly?')
        with open(options['csv'], 'r') as f:
            rows = csv.DictReader(f)
            for row in rows:
                if row['title'] != 'editorial' and row['title'] != 'impressum':
                    texts = JournalText.objects.filter(title=row['title'])
                    for text in texts:
                        authors = []
                        names   = literal_eval(row['authors'])
                        bios    = Biography.objects.all()
                        for name in names:
                            for bio in bios:
                                if bio.fullname == name:
                                    authors.append(bio.id)
                                    break
                        text.authors.set(authors)
                        text.save()
