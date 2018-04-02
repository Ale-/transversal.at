# python
import os
# django
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


"""
A manage.py command to import all objects into database
"""

class Command(BaseCommand):
    help = "Import Biography objects from a CSV file. Following columns are needed: \
            The only argument is a valid path to the CSV file."

    """
    Add CSV file as an argument to the parser
    """
    def add_arguments(self, parser):
        parser.add_argument('folder')
        parser.add_argument('--delete', default=False, help='Delete current objects')

    """
    Imports Initiative models from a given CSV file
    """
    def handle(self, *args, **options):
        if not os.path.isdir(options['folder']):
             raise CommandError('The specified folder does not exist. Have you written it properly?')
        f = options['folder']
        print("Importing biographies")
        call_command('import_biographies', f+'/biographies', delete=options['delete'])
        print("Importing blog translations")
        call_command('import_blog_translations', f+'/blog_translations', delete=options['delete'])
        print("Importing blog posts")
        call_command('import_blog_texts', f+'/blog_texts', delete=options['delete'])
        print("Importing books")
        call_command('import_books', f+'/books', delete=options['delete'])
        print("Associating media files with books")
        call_command('populate_book_files')
        print("Importing journal texts")
        call_command('import_journal_texts', f+'/journal_texts', delete=options['delete'])
        print("Associating journal texts with its authors")
        call_command('import_texts_authors', f+'/journaltexts_authors')
        print("Importing journal issues")
        call_command('import_journal_issues', f+'/journal_issues', delete=options['delete'])
        print("Associating issues with its editorials and impressums")
        call_command('import_issue_editorials', f+'/editorials_impressums')
        print("Associating journal texts with journal issues")
        call_command('populate_journal_issues', f+'/journal_issues_texts')
