# django
from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path
from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import logout
# project
from apps.views import views

urlpatterns = [
    # admin
    path('admin/', admin.site.urls),
    # logout
    url(r'^logout/$', logout, { 'next_page': '/' }, name="logout"),
    # ckeditor
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    # contact
    url(r'^contact/', include('contact_form.urls')),

    # PAGES

    # API
    # curate
    path('curate', views.APICurate.as_view(), name="api_curate"),

    # PAGES
    # front
    url(r'^$', views.Front.as_view(), name="front"),
    # books
    path('books/<slug:slug>', views.BookView.as_view(), name="book_text"),
    path('books/<slug:book_slug>/<int:pk>', views.BookExcerptView.as_view(), name="book_excerpt"),
    path('books/', views.BooksView.as_view(), name="book_texts"),
    # biographies
    path('bio/<slug:slug>', views.BioView.as_view(), name="bio"),
    # journals
    path('transversal/', views.JournalIssues.as_view(), name="journal_issues"),
    path('transversal/<slug:issue_slug>/editorial', views.JournalIssueEditorial.as_view(), name="journal_issue_editorial"),
    path('transversal/<slug:issue_slug>/impressum', views.JournalIssueImpressum.as_view(), name="journal_issue_impressum"),
    path('transversal/<slug:issue_slug>/<slug:text_slug>/<str:text_lang>', views.JournalText.as_view(), name="journal_text"),
    path('transversal/<str:slug>', views.JournalIssue.as_view(), name="journal_issue"),
    # blog
    path('blog/<slug:slug>', views.BlogTextView.as_view(), name="blog_text"),
    path('blog/<slug:source_slug>?lid=<slug:translation_slug>', views.BlogTextTranslationLegacyView.as_view(), name="blog_text_legacy"),
    path('blog/', views.BlogView.as_view(), name="blog"),
    # texts
    path('texts/', views.JournalTexts.as_view(), name="texts"),
    # events
    path('events/', views.Events.as_view(), name="events"),
    # events
    path('event/<slug:slug>', views.EventView.as_view(), name="event"),
    # search
    path('search/', views.Search.as_view(), name="search"),
    # impressum
    path('<slug:slug>', views.Page.as_view(), name="static_page"),
    # me
    path('curated-content/<int:pk>', views.CuratedContent.as_view(), name="profile"),
    # tags
    path('tag/<slug:slug>', views.TaggedContent.as_view(), name="tags"),
]

# Static and media in development
if settings.DEBUG == True:
   urlpatterns += static( settings.STATIC_URL, document_root = settings.STATIC_ROOT )
   urlpatterns += static( settings.MEDIA_URL,  document_root = settings.MEDIA_ROOT )
