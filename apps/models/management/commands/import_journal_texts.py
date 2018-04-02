# python
import sys, csv, os.path
# django
from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from django.utils.html import strip_tags
# project
from apps.models.models import Biography, JournalText, Metadata

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
        parser.add_argument('--delete', default=False, help='Delete current objects')

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
        if options['delete']:
            JournalText.objects.all().delete()
        if not os.path.isfile(options['csv']):
             raise CommandError('The specified file does not exist. Have you written it properly?')
        with open(options['csv'], 'r') as f:
            rows = csv.DictReader(f)
            for row in rows:
                translators_dids = []

                if row['translators']:
                    translators_zids = [ id for id in row['translators'].split(",") ]
                    for translator_zid in translators_zids:
                        try:
                            p = Biography.objects.get( slug=translator_zid.strip() )
                            translators_dids.append(p.pk)
                        except:
                            pass
                journal = JournalText(
                    title           = strip_tags(row['title']),
                    fulltitle       = strip_tags(row['fulltitle']),
                    subtitle        = row['subtitle'],
                    language        = row['language'],
                    date            = make_aware(parse_datetime(row['date'])),
                    body            = row['body'],
                    author_text     = row['author_text'],
                    translator_text = row['translator_text'],
                )
                journal.save()
                journal.translators.set(translators_dids)
                metadata = Metadata(
                    effective_date       = self.parseDate(row['effective_date']),
                    expiration_date      = self.parseDate(row['expiration_date']),
                    content_author       = row['creators'],
                    content_contributors = row['contributors'],
                    copyright            = row['copyright'],
                    is_published         = True,
                    source_content       = journal,
                )
                metadata.save()
