# django
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline, GenericTabularInline
from django.db.models import TextField
from django.forms import Textarea
# contrib
# from tabbed_admin import TabbedModelAdmin
# app
from . import models

admin.site.register(models.Metadata)

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
    list_display  = ('surname', 'name', 'email')
    fields = (
        ( 'surname', 'name', 'email' ),
        ( 'description')
    )
    inlines      = [ LinkInline, MetadataInline ]

admin.site.register(models.Biography, BiographyAdmin)

class JournalIssueTitleInline(admin.TabularInline):
    model = models.JournalIssueTitle
    extra = 1

class JournalTextAdmin(admin.ModelAdmin):
    model        = models.JournalText
    ordering     = ('title',)
    list_filter  = ('translators',)
    inlines      = [ MetadataInline ]

admin.site.register(models.JournalText, JournalTextAdmin)

class JournalIssueTitleInline(admin.TabularInline):
    model = models.JournalIssueTitle
    extra = 1

class JournalIssueAdmin(admin.ModelAdmin):
    model        = models.JournalIssue
    ordering     = ('title',)
    list_display = ('title', 'date')
    fields       = ('title', 'slug', 'date', 'editorial_title', 'editorial', 'impressum')
    inlines      = [ JournalIssueTitleInline, MetadataInline ]

admin.site.register(models.JournalIssue, JournalIssueAdmin)

class BlogTextTranslationInline(admin.StackedInline):
    model = models.BlogTextTranslation
    extra = 1

class BlogTextAdmin(admin.ModelAdmin):
    model        = models.BlogText
    ordering     = ('title',)
    list_display = ('title', 'author_text', 'date')
    inlines      = [ BlogTextTranslationInline, MetadataInline ]

class BlogTextTranslationAdmin(admin.ModelAdmin):
    model        = models.BlogTextTranslation
    ordering     = ('title',)
    list_display = ('title', 'author_text')
    inlines      = [ MetadataInline ]

admin.site.register(models.BlogTextTranslation, BlogTextTranslationAdmin)

admin.site.register(models.BlogText, BlogTextAdmin)

class BookAdmin(admin.ModelAdmin):
    model        = models.Book
    ordering     = ('title',)
    list_display = ('title', 'author_text')
    inlines      = [ ImageInline, MetadataInline ]

admin.site.register(models.Book, BookAdmin)

admin.site.register(models.HeaderText)
admin.site.register(models.Page)
