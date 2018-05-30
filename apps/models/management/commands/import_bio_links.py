# python
import sys, json, os.path
# django
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
# project
from apps.models.models import Biography, Link

"""
A manage.py command to update metadata
"""

class Command(BaseCommand):
    help = "Import Biography links from a JSON file. \
            The only argument is a valid path to the JSON file."

    """
    Add JSON file as an argument to the parser
    """
    def add_arguments(self, parser):
        parser.add_argument('json')
        parser.add_argument('--delete', default=False, help='Delete current objects')

    """
    Import links from a given JSON file
    """
    def handle(self, *args, **options):
        if not os.path.isfile(options['json']):
             raise CommandError('The specified file does not exist. Have you written it properly?')
        if options['delete']:
            Link.objects.filter(Q(category='p')|Q(category='b')|Q(category='t')).delete()
        with open(options['json'], 'r') as f:
            data = json.load(f)
            print(f)
            for slug in data:
                try:
                    author = Biography.objects.get(slug=slug)
                    # documents
                    if 'documents' in data[slug]:
                        for link in data[slug]['documents']:
                            l = Link(
                                url            = link['url'],
                                title          = link['title'],
                                category       = 'b',
                                description    = link['desc'],
                                source_content = author
                            )
                            l.save()
                    # publications
                    if 'publications' in data[slug]:
                        for link in data[slug]['publications']:
                            l = Link(
                                url            = link['url'],
                                title          = link['title'],
                                category       = 'p',
                                description    = link['desc'],
                                source_content = author
                            )
                            l.save()
                    # translations
                    if 'translations' in data[slug]:
                        for link in data[slug]['translations']:
                            l = Link(
                                url            = link['url'],
                                title          = link['title'],
                                category       = 't',
                                description    = link['desc'],
                                source_content = author
                            )
                            l.save()
                except Exception as e:
                    print("Problems with this bio: " + slug)
                    print(e)
