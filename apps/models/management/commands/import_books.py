# python
import sys, csv, os.path
# django
from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from django.utils.html import strip_tags
# project
from apps.models.models import Biography, Book, Metadata

"""
A manage.py command to import Book objects from a CSV file
"""

class Command(BaseCommand):
    help = "Import Book objects from a CSV file. Following columns are needed: \
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
            Book.objects.all().delete()
        if not os.path.isfile(options['csv']):
             raise CommandError('The specified file does not exist. Have you written it properly?')
        with open(options['csv'], 'r') as f:
            rows = csv.DictReader(f)
            related_books = {}
            for row in rows:
                translators_dids = []
                if row['translators']:
                    translators_zids = [ id for id in row['translators'].split(",") ]
                    for translator_zid in translators_zids:
                        try:
                            p = Biography.objects.get(slug=translator_zid.strip())
                            translators_dids.append(p.pk)
                        except:
                            pass
                authors_dids = []
                if row['authors']:
                    authors_zids = [ id for id in row['authors'].split(",") ]
                    for author_zid in authors_zids:
                        try:
                            p = Biography.objects.get(slug=author_zid.strip())
                            authors_dids.append(p.pk)
                        except:
                            pass
                title = strip_tags(row['title'])
                related_books[title] = []
                related_titles = row['related_books'].split("#")
                for t in related_titles:
                    if t:
                        related_books[title].append( t.strip() )
                book = Book(
                    title          = title,
                    slug           = row['id'],
                    date           = self.parseDate(row['date']),
                    subtitle       = row['subtitle'],
                    language       = row['language'],
                    teaser         = row['teaser'],
                    body           = row['body'],
                    author_text    = row['author_text'],
                    publisher_text = row['publisher_text'],
                    in_home        = bool(row['in_home']),
                    in_listings    = bool(row['in_listings']),
                )
                book.save()
                book.translators.set(translators_dids)
                book.authors.set(authors_dids)
                metadata = Metadata(
                    effective_date       = self.parseDate(row['effective_date']),
                    expiration_date      = self.parseDate(row['expiration_date']),
                    content_author       = row['creators'],
                    content_contributors = row['contributors'],
                    copyright            = row['copyright'],
                    is_published         = True,
                    source_content       = book,
                )
                metadata.save()
            for title in related_books:
                book = Book.objects.get(title=title)
                related = [ Book.objects.get(title=name) for name in related_books[title] ]
                book.related_books.set(related)
