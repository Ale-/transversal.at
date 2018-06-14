# python
import sys, csv, os.path, urllib.request, json
# django
from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
from django.utils.encoding import smart_str
# contrib
from bs4 import BeautifulSoup
# project
from apps.models.models import BlogText

"""
A manage.py command to import JournalIssue objects from a CSV file
"""

class Command(BaseCommand):
    help = "Import Journal objects from a CSV file. Following columns are needed: \
            The only argument is a valid path to the CSV file."

    """
    Imports JournalIssue objects from a given CSV file
    """
    def handle(self, *args, **options):
        # with open('bio_links.json', 'w', encoding='utf8') as json_file:
        blog = BlogText.objects.all()
        data = {}
        for post in blog:
            slug = post.slug
            try:
                url              = 'http://transversal.at/blog/' + slug
                data[slug]       = {}
                html_doc         = urllib.request.urlopen(url).read()
                soup             = BeautifulSoup(html_doc, 'html5lib')
                content          = soup.find("div", class_='ContentBody')
                images           = content.find_all("img")
                for img in images:
                    print(img)
            except Exception as e:
                print("---")
                print(slug)
                print(str(e))

        #json.dump(data, json_file, ensure_ascii=False)
