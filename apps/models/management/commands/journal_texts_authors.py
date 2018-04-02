# python
import sys, csv, os.path
# django
from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from django.utils.html import strip_tags
from django.db.models import Q
# project
from apps.models.models import Biography, JournalText, Metadata

"""
A manage.py command to import JournalText objects from a CSV file
"""

class Command(BaseCommand):
    help = "Import Journal objects from a CSV file. Following columns are needed: \
            The only argument is a valid path to the CSV file."

    """
    Imports Journal objects from a given CSV file
    """
    def handle(self, *args, **options):
        journal_texts = JournalText.objects.all()
        total = len(journal_texts)
        failed  = 0
        success = 0
        for text in journal_texts:
            if text.author_text:
                authors = text.author_text.split("/")
                author_ids = []
                for author_name in authors:
                    fullname = author_name.strip().split(" ")
                    if len(fullname) == 2:
                        try:
                            author  = Biography.objects.filter(Q(name=fullname[0]) & Q(surname__contains=fullname[1])).first()
                            author_ids.append( author.id )
                            success += 1
                        except Exception as e:
                            print(e)
                            print("Text with problems: " + text.title + " | Author: " + str(fullname) )
                            failed += 1
                    else:
                        print("Text skipped")
                        failed +=1
                text.authors.set(author_ids)
        print(str(failed) + " failed texts and " + str(success) + " imported texts from " + str(total))
