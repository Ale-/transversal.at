# python
from datetime import datetime
# django
from django.shortcuts import render
from django import views
from django.views.generic import ListView, DetailView
from django.utils.dateparse import parse_datetime
from django.http import Http404
# project
from apps.models import models


class Front(views.View):

    def get(self, request, *args, **kwargs):
        """ GET request """
        if request.user.is_staff:
            last_issue = models.JournalIssue.objects.all().order_by('-date').first()
            last_books = models.Book.objects.all().order_by('-date')[:3]
            blogposts  = models.BlogText.objects.all().order_by('-date')[:50]
        else:
            last_issue = models.JournalIssue.objects.filter(is_published=True).order_by('-date').first()
            last_books = models.Book.objects.filter(
                is_published=True,
                in_listings = True,
                in_home=True,
            ).order_by('-date')[:3]
            blogposts  = models.BlogText.objects.filter(is_published=True).order_by('-date')[:50]
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

        if not object.is_published and not request.user.is_staff:
            raise Http404("Post does not exist")

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

    def get_object(self, queryset=None):
        obj = super(BookView, self).get_object(queryset=queryset)
        if (not obj.is_published or not obj.in_listings) and not self.request.user.is_staff:
            raise Http404("Book does not exist")
        return obj


class BlogView(ListView):
    """View of a single blog text."""

    model = models.BlogText
    ordering = ['-date']
    paginate_by = 50

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = models.BlogText.objects.all().order_by('-date')
        else:
            queryset = models.BlogText.objects.filter(is_published=True).order_by('-date')
        return queryset

class BooksView(views.View):
    """View of a single blog text."""

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff:
            books = models.Book.objects.all().order_by('-date')
        else:
            books = models.Book.objects.filter(is_published=True, in_listings=True).order_by('-date')
        excluded_ids = []
        books_wrappers = []
        for book in books:
            if not book.id in excluded_ids:
                if book.is_published or request.user.is_staff:
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
    """View of a single journal issue."""

    def get(self, request, *args, **kwargs):
        slug = self.kwargs['slug']
        object = models.JournalIssue.objects.get(slug=slug)
        not_staff = not self.request.user.is_staff
        if not object.is_published and not_staff :
            raise Http404("Issue does not exist")
        if not_staff:
            texts  = models.JournalText.objects.filter(issue=object, is_published=True).order_by('order')
        else:
            texts  = models.JournalText.objects.filter(issue=object).order_by('order')
        texts_ordered = [ [] ]
        previous_author_text = ''
        for text in texts:
            if text.author_text != previous_author_text:
                texts_ordered[-1].append( {
                    'author' : text.author_text,
                    'titles' : [ text ],
                } )
                previous_author_text = text.author_text
            elif len(texts_ordered[-1])>0:
                texts_ordered[-1][-1]['titles'].append(text)
            if text.column_end:
                texts_ordered.append( [] )
            print(texts_ordered)

        return render(request, 'models/journalissue_detail.html', locals())

class JournalIssueEditorial(views.View):
    """View of a journal text editorial."""

    def get(self, request, *args, **kwargs):
        slug   = self.kwargs['issue_slug']
        object = models.JournalIssue.objects.get(slug=slug)
        body   = object.editorial
        title  = object.editorial_title if object.editorial_title else object.title
        html_title = "Editorial | " + object.title
        active = 'editorial'
        return render(request, 'models/journalissue_details.html', locals())

class JournalIssueImpressum(views.View):
    """View of a journal text impressum."""

    def get(self, request, *args, **kwargs):
        slug   = self.kwargs['issue_slug']
        object = models.JournalIssue.objects.get(slug=slug)
        body   = object.impressum
        title  = "Impressum"
        active = "impressum"
        html_title = "Impressum | " + object.title
        return render(request, 'models/journalissue_details.html', locals())


class JournalText(views.View):
    """View of a single journal text."""

    def get(self, request, *args, **kwargs):
        issue         = models.JournalIssue.objects.get(slug=self.kwargs['issue_slug'])
        slug          = self.kwargs['text_slug']
        lang          = self.kwargs['text_lang']
        object        = models.JournalText.objects.filter(issue=issue,slug=slug,language=lang).first()
        if not object.is_published and not request.user.is_staff :
            raise Http404("Issue does not exist")
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
