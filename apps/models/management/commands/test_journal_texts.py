# python
import sys, csv, os.path
# django
from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
from django.utils.text import slugify
from django.test import Client
from django.urls import reverse
# project
from apps.models import models

"""
A manage.py command to update metadata
"""

class Command(BaseCommand):
    help = "Import Journal objects from a CSV file. Following columns are needed: \
            The only argument is a valid path to the CSV file."

    """
    Associate journal texts with its translations
    """
    def handle(self, *args, **options):
        journal_texts = models.JournalText.objects.all()
        c = Client()
        with open('journal_texts.log', 'w') as f:
            for text in journal_texts:
                try:
                    url = reverse('journal_text', kwargs={'issue_slug': text.issue.slug, 'text_slug': text.slug, 'text_lang': text.language })
                    response = c.get(url)
                    if response.status_code != 200:
                        f.write("Problem retrieving the object : " + "\n")
                        f.write("Url: " + url + "\n")
                        f.write("\n")
                except:
                    f.write("Problem reversing text " + text.title + " with id: " + str(text.pk) + "\n" )
                    if not text.issue:
                        f.write("· Issue not defined \n")
                    if not text.slug:
                        f.write("· Slug not defined \n")
                    if not text.language:
                        f.write("· Language not defined \n")
                        f.write("\n")
            f.close()
