# python
from datetime import datetime, timezone
from itertools import chain
# django #
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.utils.timezone import now
from django.urls import reverse
from django.contrib.auth.models import User
# contrib
from ckeditor_uploader.fields import RichTextUploadingField
from adminsortable.models import SortableMixin
from gm2m import GM2MField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
# project
from .categories import LANGUAGES, TAG_CATEGORIES, LINK_CATEGORIES, ISSUE_CATEGORIES
from . import validators

validate_file_type  = validators.FileTypeValidator()

class Image(models.Model):
    """ Image """

    image_file     = models.ImageField(_('Image file'), blank=False)
    thumbnail      = ImageSpecField(source='image_file',
                                    processors=[ResizeToFill(100, 80)],
                                    format='JPEG',
                                    options={'quality': 90})
    content_type   = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id      = models.PositiveIntegerField()
    source_content = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        """String representation of this model objects."""
        return self.image_file.name


class Attachment(models.Model):
    """ Attachment """

    attachment_file = models.FileField(_('Attachment file'), blank=False,
                                        validators=[validate_file_type],
                                        upload_to='attachments')
    name            = models.CharField(_('Name of the file'), max_length=200, blank=False, null=True)
    content_type    = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id       = models.PositiveIntegerField()
    source_content  = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        """String representation of this model objects."""

        return self.attachment_file.name


class Link(models.Model):
    """ Attachment """

    url            = models.URLField(_('URL of the link'), blank=False)
    title          = models.CharField(_('Title of the link'), max_length=200, blank=True)
    category       = models.CharField(_('Category'), max_length=1, default='d', blank=False, choices=LINK_CATEGORIES)
    content_type   = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id      = models.PositiveIntegerField(null=True)
    source_content = GenericForeignKey('content_type', 'object_id')
    description    = models.CharField(_('Description'), max_length=256, blank=True, null=True)

    def __str__(self):
        """String representation of this model objects."""

        return self.url

    def get_absolute_url(self):
        return self.url


class Tag(models.Model):
    """ Attachment """

    name           = models.CharField(_('Name of the tag'), max_length=200, blank=True, unique=True)
    category       = models.CharField(_('Category of the tag'), choices=TAG_CATEGORIES, max_length=1, blank=False, default='t')
    slug           = models.SlugField(blank=True)
    description    = RichTextUploadingField(_('Description'), blank=True, null=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        """String representation of this model objects."""
        if self.category == 'f':
            return "%s [issue]" % self.name
        return self.name

    def save(self, *args, **kwargs):
        """Populate automatically 'slug' field"""
        if not self.slug:
            self.slug = slugify(self.name)

        super(Tag, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('tags', args=[self.slug])


class Biography(models.Model):
    """ Biographies of people that collaborate or work in the different texts """

    slug                 = models.SlugField(blank=True)
    name                 = models.CharField(_('Name'), max_length=200, blank=True, null=True)
    surname              = models.CharField(_('Surname'), max_length=200, blank=False, null=True)
    email                = models.EmailField(_('Email'), blank=True, null=True)
    description          = RichTextUploadingField(_('Description'), blank=True, null=True)
    comments             = models.TextField(_('Comments'), blank=True, null=True,
                                            help_text=_('Private'))
    is_published         = models.BooleanField(_('Is visible'), default=False, null=False)
    links                = GenericRelation(Link)

    class Meta:
        verbose_name = _('Biography')
        verbose_name_plural = _('Biographies')

    @property
    def fullname(self):
        if self.surname:
            return "%s %s" % (self.name, self.surname)
        return self.name

    def get_absolute_url(self):
        return reverse('bio', args=[self.slug])

    def save(self, *args, **kwargs):
        """Populate automatically 'slug' field"""
        if not self.slug:
            self.slug = slugify(self.surname)

        super(Biography, self).save(*args, **kwargs)

    def __str__(self):
        """String representation of this model objects."""

        return self.fullname


class JournalIssue(models.Model):
    """ Journal issues """

    title           = models.CharField(_('Title'), max_length=200, blank=False, null=True)
    date            = models.DateField(_('Date'), blank=True, null=True,
                                        help_text=_('Please introduce a date in the format YYYY-MM-DD or using the widget. '))
    slug            = models.SlugField(blank=True)
    editorial       = RichTextUploadingField(_('Editorial'), blank=True, null=True)
    impressum       = RichTextUploadingField(_('Impressum'), blank=True, null=True)
    links           = GenericRelation(Link)

    # metadata
    comments        = models.TextField(_('Comments'), blank=True, null=True,
                                            help_text=_('Private'))
    is_published    = models.CharField(_('Is published'), choices=ISSUE_CATEGORIES, max_length=2, default='i', null=True, blank=False)

    class Meta:
        verbose_name        = _('Journal issue')
        verbose_name_plural = _('Journal issues')
        ordering            = ('-date',)

    def get_absolute_url(self):
        return reverse('journal_issue', args=[self.slug])

    @property
    def date_id(self):
        """Id of the object based on date."""
        return self.date.strftime("%m%y")

    def save(self, *args, **kwargs):
        """Populate automatically 'slug' field"""
        if not self.slug:
            self.slug = self.date.strftime("%m%y")

        super(JournalIssue, self).save(*args, **kwargs)

    @property
    def authors(self):
        texts = self.texts.all()
        authors = {}
        return texts

    def __str__(self):
        """String representation of this model objects."""
        return self.title


class JournalIssueTitle(models.Model):
    """ Journal issue titles in other languages"""

    title = models.CharField(_('Title'), max_length=200, blank=False, null=True)
    issue = models.ForeignKey(JournalIssue, verbose_name=_('Journal issue'), related_name='titles', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _('other title')
        verbose_name_plural = _('other titles')

    def __str__(self):
        """String representation of this model objects."""
        return self.title


class JournalText(SortableMixin):
    """ Texts of the journals """

    title           = models.CharField(_('Title'), max_length=200, blank=False, null=True)
    slug            = models.SlugField(blank=True)
    fulltitle       = models.CharField(_('Full title'), max_length=200, blank=True, null=True)
    subtitle        = models.CharField(_('Subtitle'), max_length=200, blank=True, null=True)
    issue           = models.ForeignKey(JournalIssue, verbose_name=_('Journal issue'), related_name='texts', blank=False, null=True, on_delete=models.SET_NULL)
    language        = models.CharField(_('Language'), max_length=2, default='en', choices=LANGUAGES)
    date            = models.DateField(_('Date'), blank=True, null=True,
                                       help_text=_('Please introduce a date in the format YYYY-MM-DD or using the widget. '
                                                   'If you don\'t introduce a date the text will use issue\'s date'))
    body            = RichTextUploadingField(_('Body'), blank=True, null=True)
    authors         = models.ManyToManyField(Biography, verbose_name=_('Authors'), related_name='texts_created', blank=True)
    author_text     = models.CharField(_('Author attribution'), max_length=200, blank=True, null=True)
    translators     = models.ManyToManyField(Biography, verbose_name=_('Translators'), related_name='texts_translated', blank=True)
    translator_text = models.CharField(_('Translation attribution'), max_length=200, blank=True, null=True)
    translations    = models.ManyToManyField('self', blank=True)
    order           = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    column_end      = models.BooleanField(_('End of column'), default=False)
    attachments     = GenericRelation(Attachment)

    # metadata
    comments             = models.TextField(_('Comments'), blank=True, null=True,
                                            help_text=_('Private'))
    is_published         = models.BooleanField(_('Is visible'), default=True, null=False)

    class Meta:
        verbose_name = _('Journal text')
        verbose_name_plural = _('Journal texts')
        ordering = ('order',)

    @property
    def sorted_translations(self):
        return self.translations.all().order_by('language')

    def save(self, *args, **kwargs):
        """Populate automatically 'slug' field"""

        if not self.slug:
            slug = ""
            super(JournalText, self).save(*args, **kwargs)
            if self.authors.all():
                print(self.id)
                for i,author in enumerate(self.authors.all()):
                    if i>0:
                        slug += "-"
                    if author.surname:
                        slug += slugify(author.surname)
                    else:
                        slug += slugify(author.name)
            else:
                print("eh")
                slug = slugify(self.title)
            self.slug = slug
        if not self.date:
            self.date = self.issue.date

        super(JournalText, self).save(*args, **kwargs)

    def get_absolute_url(self):
        # To prevent errors when rendering lists with badly imported text
        # TODO: change this in production
        if self.issue and self.slug and self.language:
            return reverse('journal_text', args=[self.issue.slug, self.slug, self.language])
        else:
            print("El texto " + str(self.pk) + " tiene problemas")
            return None

    @property
    def get_title(self):
        return self.fulltitle if self.fulltitle else self.title

    @property
    def get_extended_title(self):
        """ Returns title + id to ease recognize texts in not-western languages """
        return "%s [%s]" % ( self.title, self.pk )

    def __str__(self):
        """String representation of this model objects."""
        return self.get_extended_title


class BlogText(models.Model):
    """ Texts of the journals """

    title           = models.CharField(_('Title'), max_length=200, blank=False, null=True)
    slug            = models.SlugField(blank=True)
    fulltitle       = models.CharField(_('Full title'), max_length=200, blank=True, null=True)
    subtitle        = models.CharField(_('Subtitle'), max_length=200, blank=True, null=True)
    language        = models.CharField(_('Language'), max_length=2, choices=LANGUAGES)
    date            = models.DateField(_('Date'), blank=True, null=True,
                                        help_text=_('Please introduce a date in the format YYYY-MM-DD or using the widget. '))
    teaser          = RichTextUploadingField(_('Teaser'), blank=True, null=True)
    body            = RichTextUploadingField(_('Body'), blank=True, null=True)
    authors         = models.ManyToManyField(Biography, verbose_name=_('Authors'),  related_name='blogposts_written', blank=True)
    author_text     = models.CharField(_('Author attribution'), max_length=200, blank=True, null=True)
    translators     = models.ManyToManyField(Biography, verbose_name=_('Translators'), related_name='blogposts_translated', blank=True)
    translator_text = models.CharField(_('Translation attribution'), max_length=200, blank=True, null=True)
    in_home         = models.BooleanField(_('Show in home'), default=True, null=False)
    in_archive      = models.BooleanField(_('Show in archive'), default=True, null=False)
    tags            = models.ManyToManyField(Tag, verbose_name=_('Tags'), related_name='blogposts_tagged', blank=True)
    attachments     = GenericRelation(Attachment)
    comments        = models.TextField(_('Comments'), blank=True, null=True,
                                            help_text=_('Private'))
    is_published    = models.BooleanField(_('Is visible'), default=True, null=False)

    def save(self, *args, **kwargs):
        """Populate automatically 'slug' field"""
        if not self.slug:
            self.slug = slugify(self.title)

        super(BlogText, self).save(*args, **kwargs)

    def get_absolute_url(self):
        try:
            url = reverse('blog_text', args=[self.slug])
            return url
        except:
            print("Texto con problemas en el slug: " + str(self.pk))
            return None

    @property
    def translated(self, *args, **kwargs):
        return len(self.translations.all())>0

    @property
    def fake_issues(self, *args, **kwargs):
        return self.tags.filter(category='f')

    @property
    def get_title(self):
        return self.fulltitle if self.fulltitle else self.title

    class Meta:
        verbose_name = _('Blog post')
        verbose_name_plural = _('Blog posts')

    def __str__(self):
        """String representation of this model objects."""
        return self.title

class BlogTextTranslation(SortableMixin):
    """ Texts of the journals """

    title           = models.CharField(_('Title'), max_length=200, blank=False, null=True)
    slug            = models.SlugField(blank=True)
    date            = models.DateField(_('Date'), blank=True, null=True,
                                        help_text=_('Please introduce a date in the format YYYY-MM-DD or using the widget. '))
    fulltitle       = models.CharField(_('Full title'), max_length=200, blank=True, null=True)
    subtitle        = models.CharField(_('Subtitle'), max_length=200, blank=True, null=True)
    language        = models.CharField(_('Language'), max_length=2, choices=LANGUAGES)
    source_text     = models.ForeignKey(BlogText, related_name='translations', verbose_name=_('Source text'), on_delete=models.SET_NULL, null=True)
    body            = RichTextUploadingField(_('Body'), blank=True, null=True)
    translator_text = models.CharField(_('Translation attribution'), max_length=200, blank=True, null=True)
    author_text     = models.CharField(_('Author attribution'), max_length=200, blank=True, null=True)
    translators     = models.ManyToManyField(Biography, verbose_name=_('Translators'), blank=True)
    order           = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    # metadata
    comments             = models.TextField(_('Comments'), blank=True, null=True,
                                            help_text=_('Private'))
    is_published         = models.BooleanField(_('Is visible'), default=True, null=False)

    def save(self, *args, **kwargs):
        """Populate automatically 'slug' field"""
        if not self.slug:
            self.slug = slugify(self.title)

        super(BlogTextTranslation, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Blog translation')
        verbose_name_plural = _('Blog translations')
        ordering = ('order',)

    def __str__(self):
        """String representation of this model objects."""
        return self.title

    def get_absolute_url(self):
        return reverse('blog_text', args=[self.slug])

    @property
    def get_title(self):
        return self.fulltitle if self.fulltitle else self.title

class Book(SortableMixin):
    """ Books """

    title              = models.CharField(_('Title'), max_length=200, blank=False, null=True)
    slug               = models.SlugField(blank=True)
    date               = models.DateField(_('Date'), blank=True, null=True,
                                           help_text=_('Please introduce a date in the format YYYY-MM-DD or using the widget. '))
    subtitle           = models.CharField(_('Subtitle'), max_length=200, blank=True, null=True)
    language           = models.CharField(_('Language'), max_length=2, choices=LANGUAGES)
    teaser             = RichTextUploadingField(_('Teaser'), blank=True, null=True)
    body               = RichTextUploadingField(_('Body'), blank=True, null=True)
    authors            = models.ManyToManyField(Biography, verbose_name=_('Authors'), related_name='books_written', blank=True)
    author_text        = models.CharField(_('Author attribution'), max_length=256, blank=False, null=True)
    translator_text    = models.CharField(_('Translators attribution'), max_length=256, blank=False, null=True)
    translators        = models.ManyToManyField(Biography, verbose_name=_('Translators'), related_name='books_translated', blank=True)
    publisher_text     = models.TextField(_('Publisher info'), max_length=200, blank=False, null=True)
    related_books      = models.ManyToManyField('self', verbose_name=_('Related publications'), blank=True)
    parent_book        = models.ForeignKey('self', verbose_name=_('Parent publication'), blank=True, null=True, on_delete=models.SET_NULL)
    in_home            = models.BooleanField(_('Show in home'), default=False, null=False)
    featured_text      = models.TextField(_('Text to be used at featured view in home'), blank=True,
                                            help_text=_('Summary to be shown in the featured view at the home. '
                                                        'In case it\'s empty author attribution will be used instead'))
    in_listings        = models.BooleanField(_('Show in listings'), default=True, null=False)
    pdf_file           = models.FileField(_('Pdf file'), blank=True, null=True)
    epub_file          = models.FileField(_('Epub file'), blank=True, null=True)
    downloads_foot     = models.TextField(_('Text below downloads'), blank=True, max_length=256)
    image              = GenericRelation(Image)
    attachments        = GenericRelation(Attachment)
    image_foot         = models.TextField(_('Text below cover image'), blank=True)
    external_url_title = models.CharField(_('Title of the main external link'), blank=True, max_length=128)
    external_url       = models.URLField(_('URL of the main external link'), blank=True)
    use_external_url   = models.BooleanField(_('Use external URL'), default=False, help_text=_('If checked user will be redirected to the external url in all listings'))

    effective_date       = models.DateField(_('Effective date'), blank=True, null=True,
                                            help_text=_('Date when the content should become available on the public site'))
    expiration_date      = models.DateField(_('Expiration date'), blank=True, null=True,
                                            help_text=_('Date when the content should no longer be visible on the public site'))
    copyright            = models.TextField(_('Copyright'), blank=True, null=True,
                                            help_text=_('A list of copyright info for this content'))
    comments             = models.TextField(_('Comments'), blank=True, null=True,
                                            help_text=_('Private'))
    is_published         = models.BooleanField(_('Is visible'), default=True, null=False)
    links                = GenericRelation(Link)
    order                = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    class Meta:
        ordering = ('order',)

    @property
    def epub_size(self):
        return self.epub_file.size

    @property
    def pdf_size(self):
        return self.pdf_file.size

    def save(self, *args, **kwargs):
        """Populate automatically 'slug' field"""
        if not self.slug:
            self.slug = slugify(self.title)
        super(Book, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('book_text', args=[self.slug])

    def __str__(self):
        """String representation of this model objects."""
        return self.title

class BookExcerpt(models.Model):
    """ Book excerpts """

    title           = models.CharField(_('Title'), max_length=200, blank=False, null=True)
    subtitle        = models.CharField(_('Subtitle'), max_length=200, blank=True, null=True)
    source_text     = models.ForeignKey(Book, related_name='excerpts', verbose_name=_('Source text'), on_delete=models.SET_NULL, null=True)
    pages           = models.CharField(_('Pages'), max_length=64, blank=True,
                                        help_text=_('Specify optionally the pages that contain the excerpt. For instance: "113-138"'))
    is_published    = models.BooleanField(_('Is visible'), default=True, null=False)

    def get_absolute_url(self):
        return self.source_text.get_absolute_url()

    class Meta:
        verbose_name = _('Essay')
        verbose_name_plural = _('Essays')

    def __str__(self):
        """String representation of this model objects."""
        return self.source_text.title + ": " + self.title

    @property
    def author_text(self):
        return self.source_text.author_text

    @property
    def date(self):
        return self.source_text.date


class HeaderText(models.Model):

    text     = RichTextUploadingField(_('Text'), blank=False, null=True)
    language = models.CharField(_('Language'), max_length=2, blank=False, choices=LANGUAGES)

    def __str__(self):
        """String representation of this model objects."""
        return self.get_language_display()

class Page(models.Model):

    title       = models.CharField(_('Title'), max_length=200, blank=False, null=True)
    content     = RichTextUploadingField(_('Text'), blank=False, null=True)
    parent_book = models.ForeignKey(Book, verbose_name='Parent book', blank=True, null=True, on_delete=models.SET_NULL)
    slug        = models.SlugField(_('Slug'), blank=False)

    def get_absolute_url(self):
        return reverse('static_page', args=[self.slug])

    def __str__(self):
        """String representation of this model objects."""
        return self.title

class Event(models.Model):
    """ Events """

    title           = models.CharField(_('Title'), max_length=200, blank=False, null=True)
    subtitle        = models.CharField(_('Subtitle'), max_length=200, blank=True, null=True)
    slug            = models.SlugField(blank=True)
    datetime        = models.DateTimeField(_('Start'), blank=False, null=True)
    end_date        = models.DateTimeField(_('End'), blank=True, null=True)
    city            = models.CharField(_('City'), max_length=128, blank=False)
    address         = models.TextField(_('Address'), max_length=256, blank=True)
    body            = RichTextUploadingField(_('Body'), blank=True, null=True)
    summary         = models.TextField(_('Summary'), blank=True, help_text=_('If this field is not empty its content will be used in listings instead of the main body'))
    is_published    = models.BooleanField(_('Is visible'), default=True, null=False)
    in_home         = models.BooleanField(_('Show in home'), default=True, null=False)
    extended_info   = models.BooleanField(_('Read more link'), default=False, null=False,
                                          help_text=_('Check this option if you want the event to have a "Read more" link connected to its section in the listings'))
    attachments     = GenericRelation(Attachment)


    def __str__(self):
        """String representation of this model objects."""
        return self.title

    def save(self, *args, **kwargs):
        """Populate automatically 'slug' field"""
        if not self.slug:
            self.slug = slugify(self.title)
        super(Event, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('event', args=[self.slug])

    @property
    def past(self):
        return self.datetime < datetime.now(timezone.utc)

class CuratedListElement(models.Model):
    """ Items in lists. """

    list           = models.ForeignKey('CuratedList', blank=False, on_delete=models.CASCADE)
    content_type   = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id      = models.PositiveIntegerField()
    source_content = GenericForeignKey('content_type', 'object_id')
    comment        = models.TextField(_('Comment'), blank=True,
                     help_text=_("An optional comment that will be displayed under "
                                 "the item in the list."))
    suggestion     = models.TextField(_('Suggestion'), blank=True,
                     help_text=_("If suggesting use this field to comment to the list owner why do "
                                 "you think this item might be included in the list"))
    user           = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    date           = models.DateField(_('Date'), default=now, blank=True,
                     help_text=_("The date the item was included in the list. The items are displayed in chronological order using this date. You can tweak the dates to change the sort order."))
    public         = models.BooleanField(_('Public'), default=False,
                    help_text=_("Select if you want the item to be publicly visible."))

    def __str__(self):
        """String representation of this model objects."""
        return "%s [%s]" % (self.list.name, self.source_content.title)


class CuratedList(models.Model):
    """ User profiles """

    user          = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    name          = models.CharField(_('Name'), max_length=128, blank=False, null=True)
    body          = RichTextUploadingField(_('Description'), blank=True, null=True,
                                           help_text=_("Provide an optional description for your list"))
    date          = models.DateField(_('Date'), default=now, blank=True)
    public        = models.BooleanField(_('Public'), default=True,
                    help_text=_("Select if you want the list to be publicly visible."))

    @property
    def username(self):
        """Returns full name of user or username"""
        user = self.user
        if user.first_name:
            return user.first_name + " " + user.last_name
        return user.username

    def get_absolute_url(self):
        return reverse('curated_list', args=[self.pk])

    @property
    def get_length(self):
        return CuratedListElement.objects.filter(list=self, public=True).count()

    @property
    def is_empty(self):
        return CuratedListElement.objects.filter(list=self, public=True).count() == 0

    def __str__(self):
        """String representation of this model objects."""
        return self.name
