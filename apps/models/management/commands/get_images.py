# python
import sys, csv, os.path, urllib.request, json
# django
from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
from django.utils.encoding import smart_str
# contrib
from bs4 import BeautifulSoup
# project
from apps.models.models import BlogText, BlogTextTranslation

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
        blog = BlogText.objects.all()
        data = {}
        for post in blog:
            # slug = post.slug
            try:
                # url              = 'http://transversal.at/blog/' + slug
                # data[slug]       = {}
                # html_doc         = urllib.request.urlopen(url).read()
                body = post.body
                soup             = BeautifulSoup(body, 'html5lib')
                # content          = soup.find("div", class_='ContentBody')
                images           = soup.find_all("img")
                if images:
                    print("---", post.title, "-", sep="\n")
                    for img in images:
                        print(img)
            except Exception as e:
                print("---", post.title, "-", sep="\n")
                print(str(e))

        #json.dump(data, json_file, ensure_ascii=False)
