# python
import string
# django
from django.contrib.admin import SimpleListFilter
# apps
from apps.models import models
from apps.models.categories import LANGUAGES


class RelatedBiographyFilter(SimpleListFilter):

    title = 'surname of     authors'
    parameter_name = 'bio'

    def lookups(self, request, model_admin):
        letters = string.ascii_lowercase
        values  = []
        for letter in letters:
            values.append((letter, letter.upper()))
        return tuple(values)

    def queryset(self, request, queryset):
        if self.value():
            persons = models.Biography.objects.filter(surname__istartswith=self.value())
            return queryset.filter(authors__in=persons)
        return queryset

class JournalTextLanguageFilter(SimpleListFilter):

    title = 'language'
    parameter_name = 'lang'

    def lookups(self, request, model_admin):
        languages = models.JournalText.objects.values_list('language', flat=True).distinct().order_by('language')
        language_dict = dict(LANGUAGES)
        values  = []
        for lang in languages:
            print(lang)
            if lang in language_dict:
                values.append((lang, language_dict[lang]))
        return tuple(values)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(language=self.value())
        return queryset

class BookLanguageFilter(SimpleListFilter):

    title = 'language'
    parameter_name = 'lang'

    def lookups(self, request, model_admin):
        languages = models.Book.objects.values_list('language', flat=True).distinct().order_by('language')
        language_dict = dict(LANGUAGES)
        values  = []
        for lang in languages:
            print(lang)
            if lang in language_dict:
                values.append((lang, language_dict[lang]))
        return tuple(values)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(language=self.value())
        return queryset

class TitleFilter(SimpleListFilter):

    title = 'title'
    parameter_name = 'title'

    def lookups(self, request, model_admin):
        letters = string.ascii_lowercase
        values  = []
        for letter in letters:
            values.append((letter, letter.upper()))
        return tuple(values)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(title__istartswith=self.value())
        else:
            return queryset


class SurnameFilter(SimpleListFilter):

    title = 'surname'
    parameter_name = 'surname'

    def lookups(self, request, model_admin):
        letters = string.ascii_lowercase
        values  = []
        for letter in letters:
            values.append((letter, letter.upper()))
        return tuple(values)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(surname__istartswith=self.value())
        return queryset

class VisibleFilter(SimpleListFilter):

    title = 'visibility'
    parameter_name = 'bio'

    def lookups(self, request, model_admin):
        return (
            ('true',  'Public' ),
            ('false', 'Not public' ),
        )

    def queryset(self, request, queryset):
        metadata = models.Metadata.objects.filter(is_published=True)
        return queryset.filter(metadata__in=metadata)
