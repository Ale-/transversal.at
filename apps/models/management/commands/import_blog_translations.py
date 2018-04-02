# python
import sys, csv, os.path
# django
from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from django.utils.html import strip_tags
from django.utils.text import slugify
# project
from apps.models.models import Biography, BlogText, BlogTextTranslation, Metadata

"""
A manage.py command to import BlogTextTranslation objects from a CSV file
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
    Imports BlogText objects from a given CSV file
    """
    def handle(self, *args, **options):
        csv.field_size_limit(sys.maxsize)
        if options['delete']:
            BlogTextTranslation.objects.all().delete()
        if not os.path.isfile(options['csv']):
             raise CommandError('The specified file does not exist. Have you written it properly?')
        with open(options['csv'], 'r') as f:
            rows = csv.DictReader(f)
            for row in rows:
                translators_dids = []
                authors_dids = []
                if row['translators']:
                    translators_zids = [ id for id in row['translators'].split(",") ]
                    for translator_zid in translators_zids:
                        try:
                            p = Biography.objects.get(slug=translator_zid.strip())
                            translators_dids.append(p.pk)
                        except:
                            pass

                post = BlogTextTranslation(
                    title           = strip_tags(row['title']),
                    slug            = row['id'],
                    fulltitle       = row['fulltitle'],
                    subtitle        = row['subtitle'],
                    language        = row['language'],
                    body            = row['body'],
                    author_text     = row['author_text'],
                    translator_text = row['translator_text'],
                )
                post.save()
                post.translators.set(translators_dids)
                metadata = Metadata(
                    effective_date       = self.parseDate(row['effective_date']),
                    expiration_date      = self.parseDate(row['expiration_date']),
                    content_author       = row['creators'],
                    content_contributors = row['contributors'],
                    copyright            = row['copyright'],
                    is_published         = False,
                    source_content       = post,
                )
                metadata.save()
