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
from django.contrib.auth.models import User
# contrib
from easy_pdf.views import PDFTemplateResponseMixin
# project
from apps.models import models, categories


class Front(views.View):

    def get(self, request, *args, **kwargs):
        """ GET request """

        if request.user.is_staff:
            last_issue  = models.JournalIssue.objects.filter(is_published='p').order_by('-date').first()
            last_books  = models.Book.objects.all().filter(
                is_published = True,
                in_home      = True,
            ).order_by('-date')[:3]
            last_events = models.Event.objects.all().filter(
                in_home=True,
                datetime__gt=datetime.now(),
            ).order_by('-datetime')[:3]
            blogposts   = models.BlogText.objects.all().order_by('-date')[:50]
        else:
            last_issue = models.JournalIssue.objects.filter(is_published='p').order_by('-date').first()
            last_books = models.Book.objects.filter(
                is_published=True,
                in_listings=True,
                in_home=True,
            ).order_by('-date')[:3]
            last_events = models.Event.objects.filter(
                is_published=True,
                datetime__gt=datetime.now(),
                in_home=True
            ).order_by('-datetime')[:3]
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

        if self.request.GET.get('hl'):
            hl = self.request.GET.get('hl')

        return render(request, 'models/blogtext_detail.html', locals())

class BlogTextTranslationLegacyView(views.View):
    """View of a single blog text."""

    def get(self, request, *args, **kwargs):
        slug = self.kwargs['translation_slug']
        object = models.BlogTextTranslation.objects.get(slug=slug)

        return render(request, 'models/blogtext_detail.html', locals())

class BlogTextPDF(PDFTemplateResponseMixin, DetailView):
    model         = models.BlogText
    template_name = 'pdf/blog-text.html'

class BlogTextTranslationPDF(PDFTemplateResponseMixin, DetailView):
    model         = models.BlogTextTranslation
    template_name = 'pdf/blog-text.html'


class BookView(DetailView):
    """View of a single blog text."""

    model = models.Book

    def get_context_data(self, **kwargs):
        context = super(BookView, self).get_context_data(**kwargs)
        if self.request.GET.get('hl'):
            context['hl'] = self.request.GET.get('hl')
        return context

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
        books = models.Book.objects.filter(parent_book__isnull=True).order_by('-date')
        return render(request, 'models/book_list.html', locals());

class BioView(views.View):
    """View of a single biography."""

    def get(self, request, slug):
        object = models.Biography.objects.get(slug=slug)

        # get texts and reorder them based on translations
        journal_texts = models.JournalText.objects.filter(authors=object).order_by('-issue__date', 'order')
        journal_text_groups = []
        last_slug  = ''
        last_issue = {}
        for text in journal_texts:
            if text.slug != last_slug or text.issue != last_issue:
                journal_text_groups.append( [text] )
                last_slug  = text.slug
                last_issue = text.issue
            else:
                journal_text_groups[-1].append(text)

        texts_translated = models.JournalText.objects.filter(translators=object)
        posts_translated = models.BlogText.objects.filter(translators=object)
        trans_translated = models.BlogTextTranslation.objects.filter(translators=object)
        books_translated = models.Book.objects.filter(translators=object)
        translations     = sorted(
            chain(texts_translated, posts_translated, trans_translated, books_translated),
            key = lambda i: getattr(i, 'title'),
        )
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

class JournalTextPDF(PDFTemplateResponseMixin, DetailView):
    model         = models.JournalText
    template_name = 'pdf/journal-text.html'

class JournalText(views.View):
    """View of a single journal text."""

    def get(self, request, *args, **kwargs):
        issue         = models.JournalIssue.objects.get(slug=self.kwargs['issue_slug'])
        slug          = self.kwargs['text_slug']
        lang          = self.kwargs['text_lang']
        object        = models.JournalText.objects.filter(issue=issue,slug=slug,language=lang).first()
        if self.request.GET.get('hl'):
            hl = self.request.GET.get('hl')
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

    def get_queryset(self):
        """ Return the list of items for this view. """

        filters = Q(datetime__gt=datetime.now())
        if self.request.user.is_anonymous:
            filters = filters & Q(is_published=True)

        return models.Event.objects.filter(filters).order_by('-datetime')

class EventView(DetailView):

    model = models.Event


class Page(DetailView):
    """View of a single static page."""

    model = models.Page


class Search(views.View):
    """ A 'searchable' view of all content """

    def get(self, request, *args, **kwargs):

        # Arguments of the query
        text   = request.GET.get('q', '')
        model  = request.GET.get('type', 'all')
        sort   = request.GET.get('sort', 'title')
        lang   = request.GET.get('lang', 'all')
        author = request.GET.get('author', 'all')

        # Set a list of current languages in searchable contents
        # TODO: reduce queries to database here, maybe cache used languages in database?
        all_languages          = dict( categories.LANGUAGES )
        journal_text_languages = [ (i['language']) for i in models.JournalText.objects.values('language').distinct() ]
        books_languages        = [ (i['language']) for i in models.Book.objects.values('language').distinct() ]
        blog_languages         = [ (i['language']) for i in models.BlogText.objects.values('language').distinct() ]
        blog_trans_languages   = [ (i['language']) for i in models.BlogTextTranslation.objects.values('language').distinct() ]
        lang_codes             = list(set( journal_text_languages + books_languages + blog_languages + blog_trans_languages))
        lang_codes.sort()
        languages              = [ (all_languages[l], l) for l in lang_codes ]
        languages.sort()

        # Set a list of current authors in searchable contents
        authors = [ (i.fullname[:30], str(i.id)) for i in models.Biography.objects.all().order_by('surname') ]

        # Create the queryset
        query             = Q()
        blog_translations = {}
        if text:
            query = query|Q(title__icontains=text)|Q(body__icontains=text)|Q(author_text__icontains=text)
        if lang != 'all':
            query = query&Q(language=lang)
        if request.user.is_anonymous:
            query = query&Q(is_published=True)
        if author != 'all':
            blog_translations = models.BlogTextTranslation.objects.filter(query&Q(source_text__authors=author)).order_by(sort)
            query = query&Q(authors=author)

        # only books
        if model == 'books':
            object_list = models.Book.objects.filter(query).order_by(sort)
        # only journal texts
        elif model == 'texts':
            object_list = models.JournalText.objects.filter(query).order_by(sort)
        # only journal texts
        elif model == 'blog':
            blog_posts        = models.BlogText.objects.filter(query).order_by(sort)
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
            content = chain(books, journal_texts, blog_texts, blog_translations)

            # chain querysets and order alphabetically
            # TODO: solve bug when sorting chained content
            if sort != '-date':
                object_list   = sorted(content, key = lambda i: getattr(i, sort))
            else:
                object_list   = sorted(content, key = lambda i: getattr(i, 'date'), reverse=True)

        # Add biographies
        if text:
            biographies = models.Biography.objects.filter(Q(name__contains=text)|Q(surname__contains=text))

        return render(request, 'models/search_list.html', locals())


class CuratedList(DetailView):
    """View of a single static page."""

    model = models.CuratedList

# class APICurate(views.View):
#     """ An API method to allow users to select their curated content """
#
#     @method_decorator(login_required)
#     def get(self, request):
#         pk              = request.GET.get('pk')
#         content_type    = ContentType.objects.get(model=request.GET.get('contenttype'))
#         content         = content_type.get_object_for_this_type(pk=pk)
#         profile,created = models.UserProfile.objects.get_or_create(user=request.user)
#         action          = request.GET.get('action')
#         if action == 'add':
#             models.ContentSelection.objects.create(
#                 content_type = content_type,
#                 object_id    = pk,
#                 profile      = profile,
#             )
#             return HttpResponse("Item added successfully to user's list of curated content")
#         models.ContentSelection.get(source_content=content).delete()
#         return HttpResponse("Item removed successfully from user's list of curated content", content_type="text/plain")

class TaggedContent(ListView):
    """View of tagged blog posts."""

    model = models.BlogText
    ordering = ['-date']
    paginate_by = 25
    template_name = 'models/tagged_content.html'

    def get_queryset(self):
        tag = models.Tag.objects.get(slug=self.kwargs.get('slug'))
        queryset = models.BlogText.objects.filter(tags=tag).order_by('-date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(TaggedContent, self).get_context_data(**kwargs)
        context['tag'] = models.Tag.objects.get(slug=self.kwargs.get('slug'))
        return context

class CuratedLists(ListView):
    """ Vief of curated lists of content. """

    model = models.CuratedList

    def get_queryset(self):
        return models.CuratedList.objects.filter(public=True).order_by('-date', 'name')

    def get_context_data(self, **kwargs):
        context = super(CuratedLists, self).get_context_data(**kwargs)
        context['personal'] = False
        return context


class UserCuratedLists(ListView):
    """ Vief of curated lists of content. """

    model = models.CuratedList

    def get_queryset(self):
        return models.CuratedList.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(UserCuratedLists, self).get_context_data(**kwargs)
        context['personal'] = True
        return context
