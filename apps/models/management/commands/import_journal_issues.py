# python
import sys, csv, os.path
# django
from django.core.management.base import BaseCommand, CommandError
# project
from apps.models.models import JournalIssue, JournalIssueTitle, Metadata

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
        parser.add_argument('--delete', default=False, help='Delete current objects')

    """
    Parses Transversal dates
    """
    def parseDate(self, date):
        return date.split()[0].replace("/", "-") if (date and date != 'None') else None

    """
    Imports JournalIssue objects from a given CSV file
    """
    def handle(self, *args, **options):
        csv.field_size_limit(sys.maxsize)
        if options['delete']:
            JournalIssue.objects.all().delete()
            JournalIssueTitle.objects.all().delete()
        if not os.path.isfile(options['csv']):
             raise CommandError('The specified file does not exist. Have you written it properly?')
        with open(options['csv'], 'r') as f:
            rows = csv.DictReader(f)
            for row in rows:
                titles = row['titles'].split('|')
                date = row['date'].split()[0].replace("/", "-")
                issue = JournalIssue(
                    title = titles[0],
                    date  = date,
                    slug  = str(date.split('-')[1] + date.split('-')[0][2:]),
                )
                print(str(date.split('-')[1] + date.split('-')[0][2:]))
                try:
                    issue.save()
                except:
                    print("rf")
                for name in titles[1:-1]:
                    title = JournalIssueTitle(
                        title = name,
                        issue = issue,
                    )
                    title.save()
                metadata = Metadata(
                    effective_date       = self.parseDate(row['effective_date']),
                    expiration_date      = self.parseDate(row['expiration_date']),
                    content_author       = row['creators'],
                    content_contributors = row['contributors'],
                    copyright            = row['copyright'],
                    is_published         = True,
                    source_content       = issue,
                )
                metadata.save()
