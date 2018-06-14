# python
import sys, csv, os.path
# django
from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from django.utils.html import strip_tags
# project
from apps.models.models import JournalText

"""
A manage.py command to import JournalText objects from a CSV file
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
    Parses Transversal dates
    """
    def parseDate(self, date):
        return date.split()[0].replace("/", "-") if (date and date != 'None') else None

    """
    Imports Journal objects from a given CSV file
    """
    def handle(self, *args, **options):
        csv.field_size_limit(sys.maxsize)
        if not os.path.isfile(options['csv']):
             raise CommandError('The specified file does not exist. Have you written it properly?')
        with open(options['csv'], 'r') as f:
            rows = csv.DictReader(f)
            for row in rows:
                title = strip_tags(row['title'])
                if row['date'] is 'None':
                    print("Date is 'None'")
                    print("Problem found in: " + title)
                else:
                    date  = self.parseDate(row['date'])
                    try:
                        text = JournalText.objects.get(title=title)
                        text.date = date
                        text.save()
                    except Exception as e:
                        print(str(e))
                        print("Problem found in: " + title)
