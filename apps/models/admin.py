# django
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.admin import GenericStackedInline, GenericTabularInline
from django.db.models import TextField
from django.forms import Textarea
from django.utils.html import format_html
from django.utils.text import slugify
from django.urls import reverse, reverse_lazy
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
# contrib
from adminsortable.admin import SortableTabularInline, NonSortableParentAdmin
# app
from . import models
from apps.utils import admin_filters as filters


def publish_issue(modeladmin, request, queryset):
    queryset.update(is_published='p')

publish_issue.short_description = "Publish selected elements"

def unpublish_issue(modeladmin, request, queryset):
    queryset.update(is_published='i')

unpublish_issue.short_description = "Unpublish selected elements"

def publish(modeladmin, request, queryset):
    queryset.update(is_published=True)

publish_issue.short_description = "Publish selected elements"

def unpublish(modeladmin, request, queryset):
    queryset.update(is_published=False)

unpublish_issue.short_description = "Unpublish selected elements"

class ImageInline(GenericTabularInline):
    model = models.Image
    extra = 0

class CategorizedLinkInline(GenericTabularInline):
    model = models.Link

    fields = (
        ( 'url', 'title' ),
        ('category', 'description')
    )
    extra = 0

class LinkInline(GenericTabularInline):
    model = models.Link

    fields = (
        ( 'url', 'title' ),
    )
    extra = 0

class AttachmentInline(GenericTabularInline):
    model = models.Attachment

    fields = (
        ( 'attachment_file', 'name' ),
    )
    extra = 0

class TagAdmin(admin.ModelAdmin):

    model = models.Tag
    list_display  = ('name', 'category', 'view')
    list_filter = ('category',)
    fields = (
        ( 'name', 'category' ),
        'description'
    )

    def view(self, obj):
        if obj.slug:
            return format_html("<a href='" + reverse('tags', args=[obj.slug]) + "'>➜</a>")
        else:
            return None
    view.short_description = 'View on site'

admin.site.register(models.Tag, TagAdmin)

class BiographyForm(forms.ModelForm):

    class Meta:
        model = models.Biography
        exclude = ()

    def clean(self):
        slug = self.cleaned_data.get('slug')
        if not slug:
            slug = slugify(self.cleaned_data.get('surname'))
        if models.Biography.objects.filter(slug=slug).exclude(id=self.instance.id).exists():
            raise forms.ValidationError(_('A biography with that slug already exists.'))
        return self.cleaned_data

class BiographyAdmin(admin.ModelAdmin):
    model    = models.Biography
    form = BiographyForm
    ordering = ('surname',)
    list_display  = ('fullname', 'email', 'is_published', 'view')
    list_filter = (filters.SurnameFilter, 'is_published')
    actions = [ publish, unpublish ]

    fieldsets = (
        ('', {
            'fields': (
                ('name', 'surname'),
                'email', 'description'
            ),
        }),
        ('Metadata', {
            'classes' : ('collapse',),
            'fields'  : (
                'slug', 'is_published', 'comments'
            ),
        })
    )

    inlines      = [ CategorizedLinkInline ]

    def view(self, obj):
        if obj.slug:
            return format_html("<a href='" + reverse('bio', args=[obj.slug]) + "'>➜</a>")
        else:
            return None
    view.short_description = 'View on site'


admin.site.register(models.Biography, BiographyAdmin)

class JournalIssueTitleInline(admin.TabularInline):
    model = models.JournalIssueTitle
    extra = 0

class JournalTextAdmin(admin.ModelAdmin):
    model             = models.JournalText

    # list
    ordering          = ('issue', 'date')
    actions           = [publish, unpublish]
    list_filter       = (filters.TitleFilter, filters.RelatedBiographyFilter, filters.JournalTextLanguageFilter, 'is_published', 'issue')
    list_display      = ('get_extended_title', 'issue', 'date', 'author_text', 'is_published')

    # form
    fieldsets = (
        ('', {
            'fields': (
                ('title','issue'),
                ('fulltitle', 'subtitle'),
                'language', 'date', 'body',
                'authors', 'author_text',
                'translations',
                'translators', 'translator_text'
            )
        }),
        ('Metadata', {
            'classes' : ('collapse',),
            'fields': (
                ('slug', 'is_published'),
                'comments'
            ),
        })
    )
    filter_horizontal = ('authors', 'translators', 'translations')
    inlines = [AttachmentInline]

admin.site.register(models.JournalText, JournalTextAdmin)

class JournalIssueTitleInline(admin.TabularInline):
    model = models.JournalIssueTitle
    extra = 0

class JournalTextInline(SortableTabularInline):
    model           = models.JournalText
    fields          = ('author_text', 'linked_title', 'language', 'column_end', 'is_published')
    readonly_fields = ('linked_title', 'author_text', 'language')
    extra = 0

    def linked_title(self, obj):
        return format_html("<a href='" + reverse('journal_text', args=[obj.issue.slug, obj.slug, obj.language]) + "'>" + obj.get_extended_title + "</a>")

    linked_title.short_description = 'Title'


class JournalIssueAdmin(NonSortableParentAdmin):
    model        = models.JournalIssue

    # list
    ordering     = ('-date', 'title',)
    list_display = ('title', 'date', 'is_published', 'view')
    list_filter  = (filters.TitleFilter, 'is_published')
    actions      = [ publish_issue, unpublish_issue ]

    # form
    fieldsets = (
        ('', {
          'fields': (('title', 'date'), 'editorial', 'impressum')
        }),
        ('Metadata', {
            'classes' : ('collapse',),
            'fields': (
                'is_published', 'slug',
                'comments'
            ),
        })
    )
    inlines      = [ JournalIssueTitleInline, LinkInline, JournalTextInline ]

    def view(self, obj):
        try:
            return format_html("<a href='" + reverse('journal_issue', args=[obj.slug]) + "'>➜</a>")
        except:
            return None
    view.short_description = 'See'


admin.site.register(models.JournalIssue, JournalIssueAdmin)

class BlogTextTranslationInline(SortableTabularInline):
    model = models.BlogTextTranslation
    fields = [ 'title', 'language', 'is_published']
    readonly_fields = ['title', 'language']
    extra = 0

class BlogTextAdmin(NonSortableParentAdmin):
    model             = models.BlogText

    # list
    ordering          = ('-date', 'title')
    list_display      = ('title', 'date', 'author_text', 'is_published')
    list_filter       = (filters.TitleFilter, filters.RelatedBiographyFilter, 'is_published')
    actions           = [ publish, unpublish ]

    # form
    fieldsets = (
        ('', {
            'fields': (
                ('title','language'),
                ('fulltitle','subtitle'),
                'date','teaser','body',
                'authors','author_text',
                'translators','translator_text',
                'tags'
            )
        }),
        ('Metadata', {
            'classes' : ('collapse',),
            'fields': (
                'slug',
                ('is_published','in_home','in_archive'),
                'comments'
            ),
        })
    )
    inlines           = [ BlogTextTranslationInline, AttachmentInline ]
    filter_horizontal = ('authors', 'translators','tags')


    def view(self, obj):
        if obj.slug:
            return format_html("<a href='" + reverse('blog_text', args=[obj.slug]) + "'>➜</a>")
        else:
            return None
    view.short_description = 'See'

class BlogTextTranslationAdmin(admin.ModelAdmin):
    model        = models.BlogTextTranslation
    ordering     = ('-source_text', 'title',)
    list_display = ('title', 'source_text')
    list_filter  = ('source_text', 'is_published')
    actions      = [ publish, unpublish ]
    filter_horizontal = ('translators',)
    inlines      = [ AttachmentInline ]

admin.site.register(models.BlogTextTranslation, BlogTextTranslationAdmin)

admin.site.register(models.BlogText, BlogTextAdmin)

class ParentBookInline(SortableTabularInline):
    model           = models.Book
    fields          = ('title', 'language', 'author_text', 'is_published')
    readonly_fields = ('title', 'author_text', 'language')
    extra = 0

class BookAdmin(NonSortableParentAdmin):
    model             = models.Book

    # list
    ordering          = ('-date', 'title',)
    list_display      = ('title', 'author_text', 'date', 'is_published', 'view')
    list_filter       = (filters.TitleFilter, filters.RelatedBiographyFilter, filters.BookLanguageFilter, 'is_published')
    actions           = [ publish, unpublish ]

    # form
    fieldsets = (
        ('', {
            'fields': (
                ('title','subtitle'),
                ('language', 'parent_book'),
                'date', 'teaser', 'featured_text', 'body',
                'authors', 'author_text', 'translators', 'publisher_text',
                ('external_url', 'external_url_title'),
                'use_external_url'
            )
        }),
        ('Files', {
            'classes' : ('collapse',),
            'fields': (
                'pdf_file', 'epub_file', 'downloads_foot', 'image_foot'
            ),
        }),
        ('Metadata', {
            'classes' : ('collapse',),
            'fields': (
                'slug',
                ('is_published','in_home','in_listings'),
                'comments',
            ),
        })
    )
    inlines           = [ ImageInline, LinkInline, ParentBookInline, AttachmentInline ]
    filter_horizontal = ('authors', 'translators',)

    def view(self, obj):
        return format_html("<a href='" + reverse('book_text', args=[obj.slug]) + "'>➜</a>")

    view.short_description = 'See'

admin.site.register(models.Book, BookAdmin)

class BookExcerptAdmin(admin.ModelAdmin):
    model        = models.BookExcerpt
    list_display = ('title', 'source', 'is_published')
    list_filter  = ('source_text',)
    ordering     = ('source_text', 'title')
    actions      = [ publish, unpublish ]

    def source(self, obj):
        if obj.source_text:
            return format_html("<a href='" + reverse('book_text', args=[obj.source_text.slug]) + "'>" + obj.source_text.title + "</a>")
        return ''

admin.site.register(models.BookExcerpt, BookExcerptAdmin)

class EventForm(forms.ModelForm):

    class Meta:
        model = models.Event
        exclude = ()

    def clean(self):
        start = self.cleaned_data.get('datetime')
        end   = self.cleaned_data.get('end_date')
        if end and end < start:
            raise forms.ValidationError('End date must happen *after* the start of the event!')
        return self.cleaned_data


class EventAdmin(admin.ModelAdmin):
    model = models.Event
    form  = EventForm
    # list
    ordering          = ('-datetime', 'title',)
    list_display      = ('title', 'datetime', 'city', 'is_published')
    list_filter       = ('is_published', 'city')
    actions           = [ publish, unpublish ]

    # form
    fieldsets = (
        ('', {
            'fields': (
                ('title', 'subtitle'),
                ('datetime', 'end_date'),
                ('city', 'address'),
                'summary',
                'body',
            )
        }),
        ('Metadata', {
            'fields': (
                'slug',
                ('is_published', 'in_home', 'extended_info'),
            ),
        })
    )
    inlines           = [ LinkInline, AttachmentInline ]


admin.site.register(models.Event, EventAdmin)
admin.site.register(models.HeaderText)

class PageForm(forms.ModelForm):
    parent_book = forms.ModelChoiceField(queryset=models.Book.objects.order_by('title'), required=False)

class PageAdmin(admin.ModelAdmin):
    model = models.Page
    form  = PageForm

admin.site.register(models.Page, PageAdmin)

class CuratedListForm(forms.ModelForm):
    books         = forms.ModelMultipleChoiceField(
        queryset = models.Book.objects.order_by('title'),
        required = False,
        widget   = FilteredSelectMultiple('Books', is_stacked=False)
    )
    book_excerpts = forms.ModelMultipleChoiceField(
        queryset = models.BookExcerpt.objects.order_by('title'),
        required = False,
        widget   = FilteredSelectMultiple('Essays', is_stacked=False)
    )
    journal_texts = forms.ModelMultipleChoiceField(
        queryset = models.JournalText.objects.order_by('title'),
        required = False,
        widget   = FilteredSelectMultiple('Journal texts', is_stacked=False)
    )
    blog_texts    = forms.ModelMultipleChoiceField(
        queryset = models.BlogText.objects.order_by('title'),
        required = False,
        widget   = FilteredSelectMultiple('Blog posts', is_stacked=False)
    )

class CuratedListAdmin(admin.ModelAdmin):
    model = models.CuratedList
    form  = CuratedListForm
    exclude           = ('user', 'length')
    list_display      = ('name', 'user', 'date', 'public')
    ordering          = ('-date',)
    list_filter       = ('public', 'user')

admin.site.register(models.CuratedList, CuratedListAdmin)
admin.site.register(models.CuratedListElement)
admin.site.register(models.Link)
