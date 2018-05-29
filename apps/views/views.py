# python
from datetime import datetime
from itertools import chain
import urllib
# django
from django.shortcuts import render
from django import views
from django.views.generic import ListView, DetailView
from django.utils.dateparse import parse_datetime
from django.http import Http404, HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
# project
from apps.models import models, categories


class Front(views.View):

    def get(self, request, *args, **kwargs):
        """ GET request """

        if request.user.is_staff:
            last_issue  = models.JournalIssue.objects.all().order_by('-date').first()
            last_books  = models.Book.objects.all().order_by('-date')[:3]
            last_events = models.Event.objects.all().filter(in_home=True).order_by('-datetime')[:3]
            blogposts   = models.BlogText.objects.all().order_by('-date')[:50]
        else:
            last_issue = models.JournalIssue.objects.filter(is_published=True).order_by('-date').first()
            last_books = models.Book.objects.filter(
                is_published=True,
                in_listings = True,
                in_home=True,
            ).order_by('-date')[:3]
            last_events = models.Event.objects.filter(is_published=True, in_home=True).order_by('-datetime')[:3]
            blogposts   = models.BlogText.objects.filter(is_published=True).order_by('-date')[:50]
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

        try:
            if not object.is_published and not request.user.is_staff:
                raise Http404("Post does not exist")
        except:
            if not object.source_text.is_published and not request.user.is_staff:
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

class BookExcerptView(DetailView):
    """View of a single blog text."""

    model = models.BookExcerpt

    def get_object(self, queryset=None):
        obj = super(BookExcerptView, self).get_object(queryset=queryset)
        if not obj.is_published and not self.request.user.is_staff:
            raise Http404("Book excerpt does not exist")
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

class BioView(views.View):
    """View of a single blog text."""

    def get(self, request, slug):
        object = models.Biography.objects.get(slug=slug)

        # get texts and reorder them based on translations
        translations = []
        texts        = models.JournalText.objects.filter(authors=object).order_by('-issue')
        pks          = []
        for text in texts:
            if text.pk not in pks:
                _translations = [text]
                for translation in text.translations.all():
                    _translations.append(translation)
                    pks.append(translation.pk)
                translations.append(_translations)
        links_publications = object.links.filter(category='p').order_by('title')
        links_translations = object.links.filter(category='t').order_by('title')
        links_documents    = object.links.filter(category='b').order_by('title')
        links_default      = object.links.filter(category='d').order_by('title')

        return render(request, 'models/biography_detail.html', locals());


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


class Events(ListView):
    """View of events. TODO: order by distance to today"""

    model    = models.Event
    ordering = ['-datetime',]


class Page(DetailView):
    """View of a single static page."""

    model = models.Page


class Search(views.View):
    """ A 'searchable' view of all content """

    def get(self, request, *args, **kwargs):

        # Arguments of the query
        text  = request.GET.get('q')
        model = request.GET.get('type')
        sort  = request.GET.get('sort')
        lang  = request.GET.get('lang')

        # Set a list of current languages in searchable contents
        # TODO: reduce queries to database here, maybe cache used languages in database?
        all_languages          = dict( categories.LANGUAGES )
        journal_text_languages = [ (i['language']) for i in models.JournalText.objects.values('language').distinct() ]
        books_languages        = [ (i['language']) for i in models.Book.objects.values('language').distinct() ]
        blog_languages         = [ (i['language']) for i in models.BlogText.objects.values('language').distinct() ]
        blog_trans_languages   = [ (i['language']) for i in models.BlogTextTranslation.objects.values('language').distinct() ]
        lang_codes             = list(set( journal_text_languages + books_languages + blog_languages + blog_trans_languages))
        lang_codes.sort()
        lang_codes.remove('')
        lang_codes.remove('sh')
        languages              = [ (all_languages[l], l) for l in lang_codes ]
        languages.sort()

        # Create the queryset
        query = Q()
        if text:
            query = query|Q(title__icontains=text)|Q(body__icontains=text)|Q(author_text__icontains=text)
        if lang != 'all':
            query = query&Q(language=lang)
        if request.user.is_anonymous:
            query = query&Q(is_published=True)

        # only books
        if model == 'books':
            object_list = models.Book.objects.filter(query).order_by(sort)
        # only journal texts
        elif model == 'texts':
            object_list = models.JournalText.objects.filter(query).order_by(sort)
        # only journal texts
        elif model == 'blog':
            blog_posts        = models.BlogText.objects.filter(query).order_by(sort)
            blog_translations = models.BlogTextTranslation.objects.filter(query).order_by(sort)
            content           = chain(blog_posts, blog_translations)

            # chain querysets and order alphabetically
            # TODO: solve bug when sorting chained content
            if sort != '-date':
                object_list   = sorted(content, key = lambda i: getattr(i, sort))
            else:
                object_list   = sorted(content, key = lambda i: getattr(i, 'date'), reverse=True)

        # everything under the sun
        else:
            books             = models.Book.objects.filter(query)
            journal_texts     = models.JournalText.objects.filter(query)
            blog_texts        = models.BlogText.objects.filter(query)
            blog_translations = models.BlogTextTranslation.objects.filter(query).order_by(sort)
            content           = chain(books, journal_texts, blog_texts, blog_translations)

            # chain querysets and order alphabetically
            # TODO: solve bug when sorting chained content
            if sort != '-date':
                object_list   = sorted(content, key = lambda i: getattr(i, sort))
            else:
                object_list   = sorted(content, key = lambda i: getattr(i, 'date'), reverse=True)


class CuratedContent(DetailView):
    """View of a single static page."""

    model = models.UserProfile


class APICurate(views.View):
    """ An API method to allow users to select their curated content """

    @method_decorator(login_required)
    def get(self, request):
        pk              = request.GET.get('pk')
        contenttype     = ContentType.objects.get(model=request.GET.get('contenttype'))
        content         = contenttype.get_object_for_this_type(pk=pk)
        profile,created = models.UserProfile.objects.get_or_create(user=request.user)
        action          = request.GET.get('action')
        if action == 'add':
            profile.curated_content.add(content)
            return HttpResponse("Item added successfully to user's list of curated content")
        profile.curated_content.remove(content)
        return HttpResponse("Item removed successfully from user's list of curated content", content_type="text/plain")

class TaggedContent(views.View):

    def get(self, request, slug):
        tag         = models.Tag.objects.get(slug=slug)
        object_list = models.BlogText.objects.filter(tags=tag)
        return render(request, 'models/tagged_content.html', locals())
