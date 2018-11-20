# python
from datetime import datetime
from itertools import chain
import urllib
# django
from django.shortcuts import render
from django import views
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.utils.dateparse import parse_datetime
from django.http import Http404, HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models.functions import Concat
from django.db.models import Value
# contrib
from easy_pdf.views import PDFTemplateResponseMixin
# project
from apps.models import models, categories
from . import forms as forms

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
            try:
                object  = models.BlogTextTranslation.objects.get(slug=slug)
                authors = object.source_text.authors.order_by('surname')
            except:
                raise Http404("Post does not exist")
        try:
            if not object.is_published and not request.user.is_staff:
                raise Http404("Post does not exist")
        except:
            if hasattr(object, 'source_text') and not object.source_text.is_published and not request.user.is_staff:
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
        context['essays'] = models.BookExcerpt.objects.filter(source_text=self.object, is_published=True)
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
        try:
            object = models.Biography.objects.get(slug=slug)
        except:
            raise Http404("Biography does not exist")

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
        try:
            object = models.JournalIssue.objects.get(slug=slug)
        except:
            raise Http404("Issue does not exist")
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
        try:
            issue         = models.JournalIssue.objects.get(slug=self.kwargs['issue_slug'])
        except:
            raise Http404("That journal text does not exist")
        slug          = self.kwargs['text_slug']
        lang          = self.kwargs['text_lang']
        object        = models.JournalText.objects.filter(issue=issue,slug=slug,language=lang).first()
        if self.request.GET.get('hl'):
            hl = self.request.GET.get('hl')
        if not object or (not object.is_published and not request.user.is_staff) :
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
            query = query|Q(title__icontains=text)|Q(body__icontains=text)|Q(author_text__icontains=text)|Q(translator_text__icontains=text)
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
            biographies = models.Biography.objects.annotate(full_name=Concat('name', Value(' '), 'surname')).filter(full_name__icontains=text)

        return render(request, 'models/search_list.html', locals())


class CuratedList(DetailView):
    """View of a single static page."""

    model = models.CuratedList

    def get_context_data(self, **kwargs):
        context = super(CuratedList, self).get_context_data(**kwargs)
        if not self.object.public and self.request.user != self.object.user:
            raise PermissionDenied
        context['items'] = models.CuratedListElement.objects.filter(list=self.object).order_by('date')
        return context


class CuratedListAdd(FormView):
    """View to create new list."""

    model         = models.CuratedList
    form_class    = forms.ListCreateForm
    template_name = 'models/curatedlist--add.html'

    def get_success_url(self):
        return reverse('user_curated_lists')

    def form_valid(self, form):
        models.CuratedList(
            user   = self.request.user,
            name   = form.cleaned_data['name'],
            body   = form.cleaned_data['body'],
            public = form.cleaned_data['public'],
        ).save()
        messages.success(self.request, "The list was created successfully")
        return super(CuratedListAdd, self).form_valid(form)

class CuratedListUpdate(UpdateView):
    """View to create new list."""

    model      = models.CuratedList
    fields     = ['name', 'body', 'public']
    template_name = 'models/curatedlist--update.html'

    def get_context_data(self, **kwargs):
        context = super(CuratedListUpdate, self).get_context_data(**kwargs)
        context['items'] = models.CuratedListElement.objects.filter(list=self.object).order_by('date')
        return context

    def form_valid(self, form):
        messages.success(self.request, "The list was updated successfully")
        return super(CuratedListUpdate, self).form_valid(form)

class CuratedListDelete(DeleteView):
    """View to add a new item to a list."""

    model = models.CuratedList

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(CuratedListDelete, self).get_object()
        if not obj.user == self.request.user:
            raise PermissionDenied
        return obj

    def get_context_data(self, **kwargs):
        context = super(CuratedListDelete, self).get_context_data(**kwargs)
        context['items'] = models.CuratedListElement.objects.filter(list=self.object).order_by('date')
        return context

    def get_success_url(self):
        return reverse('user_curated_lists')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "The list was deleted successfully")
        return super(CuratedListDelete, self).delete(request, *args, **kwargs)


class CuratedLinkAdd(FormView):
    """View to add a new item to a list."""

    form_class    = forms.ListLinkCreateForm
    template_name = 'models/curated-link--add.html'
    success_url   = '/'
    list          = CuratedList()

    def get_success_url(self):
        pk   = self.request.GET.get('list')
        list = models.CuratedList.objects.get(pk=pk)
        return list.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super(CuratedLinkAdd, self).get_context_data(**kwargs)
        pk   = self.request.GET.get('list')
        context['list']  = models.CuratedList.objects.get(pk=pk)
        context['items'] = models.CuratedListElement.objects.filter(list=pk).order_by('date')
        return context

    def form_valid(self, form):
        link = models.Link(
            url   = form.cleaned_data['url'],
            title = form.cleaned_data['title'],
        )
        link.save()
        pk   = self.request.GET.get('list')
        list = models.CuratedList.objects.get(pk=pk)
        is_suggested = self.request.user != list.user
        models.CuratedListElement(
            list           = list,
            source_content = link,
            comment        = form.cleaned_data['comment'],
            user           = self.request.user if is_suggested else None,
        ).save()
        messages.success(self.request, "The link was added/suggested to the list successfully")
        return super(CuratedLinkAdd, self).form_valid(form)

class CuratedLinkUpdate(FormView):
    """View to add a new item to a list."""

    template_name = 'models/curated-link--update.html'
    form_class    = forms.ListLinkUpdateForm

    def get_form(self):
        pk   = self.kwargs.get('pk')
        item = models.CuratedListElement.objects.get(pk=pk)
        kwargs = self.get_form_kwargs()
        kwargs['initial'] = {
            'url'     : item.source_content.url,
            'title'   : item.source_content.title,
            'comment' : item.comment,
            'date'    : item.date,
            'public'  : item.public,
        }
        return forms.ListLinkUpdateForm(**kwargs)

    def get_context_data(self, **kwargs):
        context = super(CuratedLinkUpdate, self).get_context_data(**kwargs)
        pk   = self.kwargs.get('pk')
        item = models.CuratedListElement.objects.get(pk=pk)
        context['pk']    = pk
        context['item']  = item.source_content
        context['list']  = item.list
        context['items'] = models.CuratedListElement.objects.filter(list=item.list).order_by('date')
        return context

    def form_valid(self, form):
        pk   = self.kwargs.get('pk')
        item = models.CuratedListElement.objects.get(pk=pk)
        item.date    = form.cleaned_data['date']
        item.public  = form.cleaned_data['public']
        item.comment = form.cleaned_data['comment']
        item.save()
        link = item.source_content
        link.url = form.cleaned_data['url']
        link.title = form.cleaned_data['title']
        link.save()
        self.success_url = item.list.get_absolute_url()
        messages.success(self.request, "The item was updated successfully")
        return super(CuratedLinkUpdate, self).form_valid(form)


class CuratedItemAdd(FormView):
    """View to add a new item to a list."""

    form_class    = forms.ListItemCreateForm
    template_name = 'models/curated-item--add.html'
    success_url   = '/'

    def get_form(self):
        ct = self.request.GET.get('type')
        self.id      = self.request.GET.get('pk')
        self.ct      = ContentType.objects.get(model=ct)
        self.item    = self.ct.get_object_for_this_type(pk=self.id)
        self.success_url = self.item.get_absolute_url()
        return forms.ListItemCreateForm(
            user    = self.request.user,
            item_pk = self.id,
            item_ct = self.ct,
            **self.get_form_kwargs()
        )

    def get_context_data(self, **kwargs):
        context = super(CuratedItemAdd, self).get_context_data(**kwargs)
        context['item'] = self.item
        return context

    def form_valid(self, form):
        list = form.cleaned_data['list']
        is_suggested = self.request.user != list.user
        models.CuratedListElement(
            list         = list,
            content_type = self.ct,
            object_id    = self.id,
            comment      = form.cleaned_data['comment'],
            suggestion   = form.cleaned_data['suggestion'],
            user         = self.request.user if is_suggested else None,
            public       = form.cleaned_data['public'],
        ).save()
        if is_suggested:
            email = EmailMessage(
                subject='You\'ve received a suggestion in transversal.at',
                body="Transversal user «%s» [%s] has suggested a new item for your "
                "list «%s». You can check the suggestion visiting your profile at: %s" % (
                    self.request.user,
                    self.request.user.email,
                    list.name,
                    "https://transversal.at/curated-content/me"
                ),
                to=[ list.user.email ]
            )
            email.send()

        messages.success(self.request, "The item was added/suggested to the list successfully")
        return super(CuratedItemAdd, self).form_valid(form)

class CuratedItemUpdate(UpdateView):
    """View to add a new item to a list."""

    model         = models.CuratedListElement
    template_name = 'models/curated-item--update.html'
    fields        = ['comment', 'date', 'public']
    success_url   = '/'

    def get_success_url(self):
        return self.object.list.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super(CuratedItemUpdate, self).get_context_data(**kwargs)
        context['item'] = self.object.source_content
        context['list'] = self.object.list
        context['items'] = models.CuratedListElement.objects.filter(list=self.object.list).order_by('date')
        return context

    def form_valid(self, form):
        messages.success(self.request, "The item was updated successfully")
        return super(CuratedItemUpdate, self).form_valid(form)


class CuratedItemDelete(DeleteView):
    """View to add a new item to a list."""

    model         = models.CuratedListElement

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(CuratedItemDelete, self).get_object()
        if not obj.list.user == self.request.user:
            raise PermissionDenied
        return obj

    def get_success_url(self):
        return self.object.list.get_absolute_url()

    def delete(self, request, *args, **kwargs):
        obj  = super(CuratedItemDelete, self).get_object()
        messages.success(self.request, "The item was removed from the list successfully")
        return super(CuratedItemDelete, self).delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CuratedItemDelete, self).get_context_data(**kwargs)
        context['item'] = self.object.source_content
        context['list'] = self.object.list
        context['items'] = models.CuratedListElement.objects.filter(list=self.object.list).order_by('date')
        return context

class CuratedLinkDelete(CuratedItemDelete):
    """View to add a new item to a list."""

    model         = models.CuratedListElement

    def delete(self, request, *args, **kwargs):
        obj  = super(CuratedLinkDelete, self).get_object()
        obj.source_content.delete()
        messages.success(self.request, "The item was removed from the list successfully")
        return super(CuratedItemDelete, self).delete(request, *args, **kwargs)

class Contact(FormView):

    form_class    = forms.ContactForm
    template_name = 'contact_form/contact_form.html'

    @method_decorator(login_required)
    def get(self, request, *arg, **kwargs):
        return super(Contact, self).get(self, request, *arg, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Contact, self).get_context_data(**kwargs)
        user = User.objects.get(pk=self.kwargs.get('pk'))
        context['recipient'] = user.username
        return context

    def form_valid(self, form):
        user = User.objects.get(pk=self.kwargs.get('pk'))
        email = EmailMessage(
            subject=form.cleaned_data['subject'],
            body= "%s %s %s %s %s %s%s" % (
                "<p>The user of transversal.at",
                user.username,
                "has sent you an email using platform's contact form:</p><p>",
                form.cleaned_data['body'],
                "</p><p>You can reply him here:",
                reverse('contact', args=[self.request.user.pk]),
                "</p>"
            ),
            to=[ user.email ]
        )
        email.send()
        messages.success(self.request, "The email was sent successfully")
        self.success_url = reverse('user_curated_lists')
        return super(Contact, self).form_valid(form)

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
        if self.request.user.is_anonymous:
          raise PermissionDenied    
        return models.CuratedList.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(UserCuratedLists, self).get_context_data(**kwargs)
        context['suggestions'] = models.CuratedListElement.objects.filter(user=self.request.user).order_by('-date')
        context['personal'] = True
        return context


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
