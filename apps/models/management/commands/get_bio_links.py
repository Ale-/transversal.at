# python
import sys, csv, os.path, urllib.request, json
# django
from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
from django.utils.encoding import smart_str
# contrib
from bs4 import BeautifulSoup
# project
from apps.models.models import Biography

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
        with open('bio_links.json', 'w', encoding='utf8') as json_file:
            bios = Biography.objects.all()
            data = {}
            for bio in bios:
                slug = bio.slug
                try:
                    url              = 'http://transversal.at/bio/' + slug
                    data[slug]       = {}
                    html_doc         = urllib.request.urlopen(url).read()
                    soup             = BeautifulSoup(html_doc, 'html5lib')
                    titles           = soup.find_all("h4")
                    for title in titles:
                        title_text = title.get_text()
                        data[slug][title_text] = []
                        container = title.parent
                        links = container.find_all('a')
                        for link in links:
                            href = link.get('href')
                            try:
                                desc = link.find_next('span').get_text().strip()
                            except:
                                desc = None
                            if not href.startswith('/transversal') and not href.startswith('http://transversal.at/') and not href.startswith('/blog'):
                                data[slug][title_text].append({
                                    'title' : link.get_text().strip(),
                                    'url'   : href,
                                    'desc'  : desc
                                })
                except Exception as e:
                    print("---")
                    print(slug)
                    print(str(e))
                    data[slug] = "Check"

            json.dump(data, json_file, ensure_ascii=False)
