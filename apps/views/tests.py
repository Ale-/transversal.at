# Import generic python packages
import json
# Import django packages
from django.test import Client
from django.test import TestCase
from django.urls import reverse
# Import site apps
from apps.models import models

class ViewsTest(TestCase):
    """ Test access to views """

    def test_journal_texts(self):
        """
        Check journal text views
        """

        journal_texts = models.JournalText.objects.all()
        print( len(journal_texts) )
        c = Client()
        for text in journal_texts:
            print(text.slug)
            response = c.get(reverse('journal_text', kwargs={'issue_slug': text.issue.slug, 'text_slug': text.slug, 'text_lang': text.language }))
            self.assertEqual(response.status_code, 200)
