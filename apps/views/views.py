# python
from datetime import datetime
# django
from django.shortcuts import render
from django import views
from django.views.generic import ListView, DetailView
from django.utils.dateparse import parse_datetime
# project
from apps.models import models


class Front(views.View):

    def get(self, request, *args, **kwargs):
        """ GET request """

        last_issue = models.JournalIssue.objects.order_by('-date').first()
        last_books = models.Book.objects.order_by('-date')[:3]
        blogposts  = models.BlogText.objects.order_by('-date')[:50]
        return render(request, 'pages/front.html', locals())

class BlogTextView(views.View):
    """View of a single blog text."""

    def get(self, request, *args, **kwargs):
        slug    = self.kwargs['slug']
        try:
            object  = models.BlogText.objects.get(slug=slug)
            authors = object.authors.order_by('surname')
        except:
            object  = models.BlogTextTranslation.objects.get(slug=slug)
            authors = object.source_text.authors.order_by('surname')
        return render(request, 'models/blogtext_detail.html', locals())

class BlogTextTranslationLegacyView(views.View):
    """View of a single blog text."""

    def get(self, request, *args, **kwargs):
        slug = self.kwargs['translation_slug']
        object = models.BlogTextTranslation.objects.get(slug=slug)

        return render(request, 'models/blogtext_detail.html', locals())

class BookView(DetailView):
    """View of a single blog text."""

    model = models.Book

class BlogView(ListView):
    """View of a single blog text."""

    model = models.BlogText
    ordering = ['-date']
    paginate_by = 50

class BooksView(views.View):
    """View of a single blog text."""

    def get(self, request, *args, **kwargs):
        books = models.Book.objects.all().order_by('-date')
        excluded_ids = []
        books_wrappers = []
        for book in books:
            if not book.id in excluded_ids:
                if book.metadata.first().is_published or request.user.is_staff:
                    wrapper = [ book ]
                    for related_book in book.related_books.all():
                            print(related_book.id)
                            wrapper.append(related_book)
                            excluded_ids.append(related_book.id)
                    books_wrappers.append(wrapper)
        return render(request, 'models/book_list.html', locals());

class BioView(DetailView):
    """View of a single blog text."""

    model = models.Biography


class JournalIssues(ListView):
    """View of a single blog text."""

    model = models.JournalIssue
    ordering = ['-date']

class JournalIssue(views.View):
    """View of a single blog text."""

    def get(self, request, *args, **kwargs):
        slug = self.kwargs['slug']
        object = models.JournalIssue.objects.get(slug=slug)
        texts  = models.JournalText.objects.filter(issue=object).order_by('author_text')
        texts_ordered = {}
        for text in texts:
            if not text.author_text in texts_ordered:
                texts_ordered[text.author_text] = [ text]
            else:
                texts_ordered[text.author_text].append(text);
        print(texts_ordered)
        return render(request, 'models/journalissue_detail.html', locals())

class JournalIssueEditorial(views.View):
    """View of a single blog text."""

    def get(self, request, *args, **kwargs):
        slug   = self.kwargs['issue_slug']
        object = models.JournalIssue.objects.get(slug=slug)
        body   = object.editorial
        title  = object.editorial_title if object.editorial_title else object.title
        html_title = "Editorial | " + object.title
        active = 'editorial'
        return render(request, 'models/journalissue_details.html', locals())

class JournalIssueImpressum(views.View):
    """View of a single blog text."""

    def get(self, request, *args, **kwargs):
        slug   = self.kwargs['issue_slug']
        object = models.JournalIssue.objects.get(slug=slug)
        body   = object.impressum
        title  = "Impressum"
        active = "impressum"
        html_title = "Impressum | " + object.title
        return render(request, 'models/journalissue_details.html', locals())


class JournalText(views.View):
    """View of a single blog text."""

    def get(self, request, *args, **kwargs):
        slug          = self.kwargs['text_slug']
        object        = models.JournalText.objects.filter(slug=slug).first()
        # related_texts = models.JournalText.objects.filter(author=author)
        return render(request, 'models/journaltext_detail.html', locals())


class JournalTexts(views.View):
    """View of a single blog text."""

    def get(self, request, *args, **kwargs):
        object_list  = models.JournalText.objects.filter(authors__isnull=True)
        # related_texts = models.JournalText.objects.filter(author=author)
        return render(request, 'models/journaltexts.html', locals())

class Page(DetailView):
    """View of a single static page."""

    model = models.Page
