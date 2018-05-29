# django
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline, GenericTabularInline
from django.db.models import TextField
from django.forms import Textarea
from django.utils.html import format_html
from django.urls import reverse
# contrib
from adminsortable.admin import SortableTabularInline, NonSortableParentAdmin
# app
from . import models
from apps.utils import admin_filters as filters


def publish(modeladmin, request, queryset):
    for obj in queryset:
        obj.is_published = True
        obj.save()

publish.short_description = "Publish selected elements"

def unpublish(modeladmin, request, queryset):
    for obj in queryset:
        obj.is_published = False
        obj.save()

unpublish.short_description = "Unpublish selected elements"

class ImageInline(GenericTabularInline):
    model = models.Image
    extra = 1

class CategorizedLinkInline(GenericTabularInline):
    model = models.Link

    fields = (
        ( 'url', 'title' ),
        ('category', 'description')
    )
    extra = 1

class LinkInline(GenericTabularInline):
    model = models.Link

    fields = (
        ( 'url', 'title' ),
    )
    extra = 1


class TagAdmin(admin.ModelAdmin):

    model = models.Tag
    list_display  = ('name', 'category', 'view')
    list_filter = ('category',)
    fields = (
        ( 'name', 'category' ),
    )

    def view(self, obj):
        if obj.slug:
            return format_html("<a href='" + reverse('tags', args=[obj.slug]) + "'>➜</a>")
        else:
            return None
    view.short_description = 'View on site'

admin.site.register(models.Tag, TagAdmin)


class BiographyAdmin(admin.ModelAdmin):
    model    = models.Biography
    ordering = ('name',)
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
                'is_published',
                ('effective_date', 'expiration_date'),
                ('content_author', 'content_contributors'),
                'copyright','comments'
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
    extra = 1

class JournalTextAdmin(admin.ModelAdmin):
    model             = models.JournalText

    # list
    ordering          = ('issue', 'title')
    actions           = [publish, unpublish]
    list_filter       = (filters.TitleFilter, filters.RelatedBiographyFilter, filters.JournalTextLanguageFilter, 'is_published')
    list_display      = ('title', 'issue', 'date', 'author_text', 'view', 'is_published')

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
                ('effective_date','expiration_date'),
                ('content_author','content_contributors'),
                'copyright','comments'
            ),
        })
    )
    filter_horizontal = ('authors', 'translators', 'translations')

    def view(self, obj):
        try:
            return format_html("<a href='" + reverse('journal_text', args=[obj.issue.slug, obj.slug]) + "'>➜</a>")
        except:
            return None
    view.short_description = 'See'

admin.site.register(models.JournalText, JournalTextAdmin)

class JournalIssueTitleInline(admin.TabularInline):
    model = models.JournalIssueTitle
    extra = 1

class JournalTextInline(SortableTabularInline):
    model           = models.JournalText
    fields          = ('title', 'author_text', 'column_end')
    readonly_fields = ('title', 'author_text')
    extra = 1

class JournalIssueAdmin(NonSortableParentAdmin):
    model        = models.JournalIssue

    # list
    ordering     = ('-date', 'title',)
    list_display = ('title', 'date', 'view')
    list_filter  = (filters.TitleFilter, 'is_published')
    actions      = [ publish, unpublish ]

    # form
    fieldsets = (
        ('', {
          'fields': (('title', 'date'), 'editorial_title', 'editorial', 'impressum')
        }),
        ('Metadata', {
            'classes' : ('collapse',),
            'fields': (
                'is_published',
                ('effective_date','expiration_date'),
                ('content_author','content_contributors'),
                'copyright','comments'
            ),
        })
    )
    inlines      = [ JournalIssueTitleInline, JournalTextInline ]

    def view(self, obj):
        try:
            return format_html("<a href='" + reverse('journal_issue', args=[obj.slug]) + "'>➜</a>")
        except:
            return None
    view.short_description = 'See'


admin.site.register(models.JournalIssue, JournalIssueAdmin)

class BlogTextTranslationInline(admin.StackedInline):
    model = models.BlogTextTranslation
    extra = 0

class BlogTextAdmin(admin.ModelAdmin):
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
                ('is_published','in_home','in_archive'),
                ('effective_date','expiration_date'),
                ('content_author','content_contributors'),
                'copyright','comments'
            ),
        })
    )
    inlines           = [ BlogTextTranslationInline ]
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
    actions      = [ publish, unpublish ]

admin.site.register(models.BlogTextTranslation, BlogTextTranslationAdmin)

admin.site.register(models.BlogText, BlogTextAdmin)

class BookAdmin(admin.ModelAdmin):
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
                'language', 'date', 'teaser', 'body',
                'authors', 'author_text', 'featured_text', 'translators', 'publisher_text',
                'related_books', 'pdf_file', 'epub_file', 'downloads_foot', 'image_foot',
                ('external_url', 'external_url_title'), 'use_external_url'
            )
        }),
        ('Metadata', {
            'classes' : ('collapse',),
            'fields': (
                ('is_published','in_home','in_listings'),
                ('effective_date','expiration_date'),
                ('content_author','content_contributors'),
                'copyright','comments',
            ),
        })
    )
    inlines           = [ ImageInline, LinkInline ]
    filter_horizontal = ('authors', 'translators', 'related_books')

    def view(self, obj):
        return format_html("<a href='" + reverse('book_text', args=[obj.slug]) + "'>➜</a>")

    view.short_description = 'See'

admin.site.register(models.Book, BookAdmin)

class BookExcerptAdmin(admin.ModelAdmin):
    model = models.BookExcerpt

admin.site.register(models.BookExcerpt, BookExcerptAdmin)

class EventAdmin(admin.ModelAdmin):
    model = models.Event
    # list
    ordering          = ('-datetime', 'title',)
    list_display      = ('title', 'datetime', 'city', 'is_published')
    list_filter       = ('is_published', 'city')
    actions           = [ publish, unpublish ]

    # form
    fieldsets = (
        ('', {
            'fields': (
                ('title', 'datetime'),
                ('city', 'address'),
                'body',
            )
        }),
        ('Metadata', {
            'fields': (
                ('is_published', 'in_home',),
            ),
        })
    )
    inlines           = [ LinkInline ]


admin.site.register(models.Event, EventAdmin)

admin.site.register(models.HeaderText)
admin.site.register(models.Page)
