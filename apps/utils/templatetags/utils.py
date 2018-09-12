# python
import os, re
# django
from django import template
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType
# project
from django.conf import settings
from apps.models import models

register = template.Library()

@register.simple_tag
def css(file):
    return  settings.STATIC_URL + settings.PROJECT_STATIC_FOLDER + '/css/' + file

@register.simple_tag
def js(file):
    return  settings.STATIC_URL + settings.PROJECT_STATIC_FOLDER + '/js/' + file

@register.simple_tag
def bower(path):
    return  settings.STATIC_URL + settings.PROJECT_STATIC_FOLDER + '/js/bower_components/' + path

@register.simple_tag
def img(file):
    return  settings.STATIC_URL + settings.PROJECT_STATIC_FOLDER + '/img/' + file

@register.inclusion_tag('fake-breadcrumb.html')
def fake_breadcrumb(text=_("Go back to previous page")):
    return { 'text' : text }

@register.simple_tag
def last_date(queryset):
    n = len(queryset)
    date = getattr(queryset[n-1], 'date')
    return date.strftime("%m/%Y") if date else ""

@register.filter
def order_by(queryset, args):
    args = [x.strip() for x in args.split(',')]
    return queryset.order_by(*args)

@register.filter
def verbose_name(obj):
    return obj._meta.verbose_name

@register.filter
def contenttype(obj):
    return obj.__class__.__name__.lower()

@register.filter
def verbose_name_slug(obj):
    return slugify(obj._meta.verbose_name)

@register.filter
def is_curated(obj, user):
    profile = models.UserProfile.objects.get(user=user)
    if profile:
        return obj in profile.curated_content.all()
    return False

@register.filter
def filesize(url):
    print( print(settings.BASE_DIR + url) )
    return os.path.getsize(settings.BASE_DIR + url)

@register.filter
def sort_by(queryset, order):
    return queryset.order_by(order)

@register.filter
def googlify(text):
    value = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return mark_safe(re.sub(r'[-\s]+', '+', text))

@register.simple_tag
def rtl(langcode):
    if langcode in ['ar', 'fa', 'he', 'az', 'ku', 'ur']:
        return 'dir=rtl'
    else:
        return ' '

@register.filter
def any_is_published(queryset):
    for item in queryset:
        if item.is_published:
            return True
    return False
