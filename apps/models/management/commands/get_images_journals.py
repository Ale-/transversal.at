# python
import sys, csv, os.path, urllib.request, json
# django
from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
from django.utils.encoding import smart_str
# contrib
from bs4 import BeautifulSoup
# project
from apps.models.models import JournalText

"""
A manage.py command to import JournalIssue objects from a CSV file
"""

class Command(BaseCommand):
    """
    Get images from journal texts
    """
    def handle(self, *args, **options):
        texts = JournalText.objects.all()
        for post in texts:
            try:
                body = post.body
                soup             = BeautifulSoup(body, 'html5lib')
                images           = soup.find_all("img")
                if images:
                    # print("---", post.title, "-", sep="\n")
                    for img in images:
                        print(img["src"])
            except Exception as e:
                #print("---", post.title, "-", sep="\n")
                #print(str(e))  
                pass
