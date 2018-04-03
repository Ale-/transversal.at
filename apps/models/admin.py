# django
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline, GenericTabularInline
from django.db.models import TextField
from django.forms import Textarea
from django.utils.html import format_html
from django.urls import reverse
# app
from . import models
from apps.utils import admin_filters as filters

admin.site.register(models.Metadata)


def publish(modeladmin, request, queryset):
    for obj in queryset:
        meta = obj.metadata.first()
        if not meta.is_published:
            meta.is_published = True
            meta.save()

publish.short_description = "Publish selected elements"

def unpublish(modeladmin, request, queryset):
    for obj in queryset:
        meta = obj.metadata.first()
        if meta.is_published:
            meta.is_published = False
            meta.save()

unpublish.short_description = "Unpublish selected elements"

class ImageInline(GenericTabularInline):
    model = models.Image
    extra = 1

class LinkInline(GenericTabularInline):
    model = models.Link

    fields = (
        ( 'url', 'title' ),
    )
    extra = 1

class MetadataInline(GenericStackedInline):
    model = models.Metadata
    formfield_overrides = {
        TextField: {'widget': Textarea( attrs={'rows': 1, 'cols': 40} )},
    }

    fields = (
        ( 'is_published', 'expiration_date', 'effective_date' ),
        ('content_author', 'content_contributors' ),
        ('copyright', 'comments')
    )
    extra = 1

    def get_extra (self, request, obj=None, **kwargs):
        """Dynamically sets the number of extra forms. 0 if the related object
        already exists or the extra configuration otherwise."""
        if obj:
            # Don't add any extra forms if the related object already exists.
            return 0
        return self.extra

class BiographyAdmin(admin.ModelAdmin):
    model    = models.Biography
    ordering = ('name',)
    list_display  = ('name', 'surname', 'email', 'published', 'view')
    list_filter = (filters.SurnameFilter,)
    actions = [ publish, unpublish ]
    fields = (
        ( 'name', 'surname' ),
        ( 'email' ),
        ( 'description' )
    )
    inlines      = [ LinkInline, MetadataInline ]

    def view(self, obj):
        if obj.slug:
            return format_html("<a href='" + reverse('bio', args=[obj.slug]) + "'>➜</a>")
        else:
            return None
    view.short_description = 'View on site'

    def published(self, obj):
        return "✓" if obj.metadata.first().is_published else "❌"

admin.site.register(models.Biography, BiographyAdmin)

class JournalIssueTitleInline(admin.TabularInline):
    model = models.JournalIssueTitle
    extra = 1

class JournalTextAdmin(admin.ModelAdmin):
    model             = models.JournalText
    ordering          = ('issue', 'title')
    list_filter       = (filters.TitleFilter, filters.RelatedBiographyFilter, filters.JournalTextLanguageFilter)
    list_display      = ('title', 'issue', 'date', 'author_text', 'view')
    inlines           = [ MetadataInline ]
    actions           = [ publish, unpublish ]
    filter_horizontal = ('authors', 'translators')

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

class JournalIssueAdmin(admin.ModelAdmin):
    model        = models.JournalIssue
    ordering     = ('-date', 'title',)
    list_display = ('title', 'date')
    list_filter  = (filters.TitleFilter,)
    fields       = ('title', 'slug', 'date', 'editorial_title', 'editorial', 'impressum')
    actions      = [ publish, unpublish ]
    inlines      = [ JournalIssueTitleInline, MetadataInline ]

admin.site.register(models.JournalIssue, JournalIssueAdmin)

class BlogTextTranslationInline(admin.StackedInline):
    model = models.BlogTextTranslation
    extra = 0

class BlogTextAdmin(admin.ModelAdmin):
    model             = models.BlogText
    ordering          = ('-date', 'title')
    list_display      = ('title', 'date', 'author_text', 'published')
    list_filter       = (filters.TitleFilter, filters.RelatedBiographyFilter,)
    inlines           = [ BlogTextTranslationInline, MetadataInline ]
    actions           = [ publish, unpublish ]
    filter_horizontal = ('authors', 'translators')

    def published(self, obj):
        return "✓" if obj.metadata.first().is_published else "❌"

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
    inlines      = [ MetadataInline ]

admin.site.register(models.BlogTextTranslation, BlogTextTranslationAdmin)

admin.site.register(models.BlogText, BlogTextAdmin)

class BookAdmin(admin.ModelAdmin):
    model             = models.Book
    ordering          = ('-date', 'title',)
    list_display      = ('title', 'author_text', 'date', 'published', 'view')
    list_filter       = (filters.TitleFilter, filters.RelatedBiographyFilter, filters.BookLanguageFilter,)
    inlines           = [ ImageInline, MetadataInline ]
    actions           = [ publish, unpublish ]
    filter_horizontal = ('authors', 'translators', 'related_books')

    def published(self, obj):
        return "✓" if obj.metadata.first().is_published else "❌"

    def view(self, obj):
        return format_html("<a href='" + reverse('book_text', args=[obj.slug]) + "'>➜</a>")
    view.short_description = 'See'

admin.site.register(models.Book, BookAdmin)

admin.site.register(models.HeaderText)
admin.site.register(models.Page)
