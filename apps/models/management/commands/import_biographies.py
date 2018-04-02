# django
from ast import literal_eval
# python
import csv, os.path
# django
from django.core.management.base import BaseCommand, CommandError
# project
from apps.models.models import Biography, Metadata, Link

"""
A manage.py command to import Biography objects from a CSV file
"""

class Command(BaseCommand):
    help = "Import Biography objects from a CSV file. Following columns are needed: \
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
    Imports Initiative models from a given CSV file
    """
    def handle(self, *args, **options):
        if options['delete']:
            Biography.objects.all().delete()
            Metadata.objects.all().delete()
            Link.objects.all().delete()
        if not os.path.isfile(options['csv']):
             raise CommandError('The specified file does not exist. Have you written it properly?')
        with open(options['csv'], 'r') as f:
            rows = csv.DictReader(f)
            for row in rows:
                if(row['name']):
                    bio = Biography(
                         slug        = row['id'].strip(),
                         name        = row['name'].strip(),
                         surname     = row['surname'].strip(),
                         email       = row['email'].strip(),
                         description = row['description'].strip(),
                    )
                else:
                    bio = Biography(
                         slug        = row['id'].strip(),
                         name        = row['surname'].strip(),
                         email       = row['email'].strip(),
                         description = row['description'].strip(),
                    )

                bio.save()
                metadata = Metadata(
                    effective_date       = self.parseDate(row['effective_date']),
                    expiration_date      = self.parseDate(row['expiration_date']),
                    content_author       = row['creators'],
                    content_contributors = row['contributors'],
                    copyright            = row['copyright'],
                    comments             = row['comment'],
                    is_published         = True,
                    source_content       = bio,
                )
                metadata.save()
                links =  literal_eval('[' + row['external_links'] + ']')
                for link in links:
                    l = Link(
                        url            = link['link_target'],
                        title          = link['link_title'],
                        source_content = bio,
                    )
                    l.save()
