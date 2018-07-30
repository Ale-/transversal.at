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
    # path('curate', views.APICurate.as_view(), name="api_curate"),

    # PAGES
    # front
    url(r'^$', views.Front.as_view(), name="front"),
    # books
    path('books/<slug:slug>', views.BookView.as_view(), name="book_text"),
    path('books/<slug:book_slug>/excerpts/<slug:slug>', views.BookExcerptView.as_view(), name="book_excerpt"),
    path('books/', views.BooksView.as_view(), name="book_texts"),
    # biographies
    path('bio/<slug:slug>', views.BioView.as_view(), name="bio"),
    # journals
    path('transversal/', views.JournalIssues.as_view(), name="journal_issues"),
    path('transversal/<slug:issue_slug>/editorial', views.JournalIssueEditorial.as_view(), name="journal_issue_editorial"),
    path('transversal/<slug:issue_slug>/impressum', views.JournalIssueImpressum.as_view(), name="journal_issue_impressum"),
    path('transversal/<slug:issue_slug>/<slug:text_slug>/<str:text_lang>', views.JournalText.as_view(), name="journal_text"),
    path('transversal/pdf/journal-text/<int:pk>/', views.JournalTextPDF.as_view(), name="journal_text_pdf"),
    path('transversal/<str:slug>', views.JournalIssue.as_view(), name="journal_issue"),
    # blog
    path('blog/<slug:slug>', views.BlogTextView.as_view(), name="blog_text"),
    path('transversal/pdf/blog/<int:pk>/', views.BlogTextPDF.as_view(), name="blog_text_pdf"),
    path('transversal/pdf/blog_translation/<int:pk>/', views.BlogTextTranslationPDF.as_view(), name="blog_text_translation_pdf"),
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
    # user lists
    path('curated-content/', views.CuratedLists.as_view(), name="curated_lists"),
    # user lists
    path('curated-content/me', views.UserCuratedLists.as_view(), name="user_curated_lists"),
    # me
    path('curated-content/<int:pk>', views.CuratedList.as_view(), name="curated_list"),
    # tags
    path('tag/<slug:slug>', views.TaggedContent.as_view(), name="tags"),
    # static pages
    path('<slug:slug>', views.Page.as_view(), name="static_page"),
]

# Static and media in development
if settings.DEBUG == True:
   urlpatterns += static( settings.STATIC_URL, document_root = settings.STATIC_ROOT )
   urlpatterns += static( settings.MEDIA_URL,  document_root = settings.MEDIA_ROOT )
