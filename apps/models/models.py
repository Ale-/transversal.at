# python
from datetime import datetime, timezone
# django #
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User
# contrib
from ckeditor_uploader.fields import RichTextUploadingField
from adminsortable.models import SortableMixin
from gm2m import GM2MField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
# project
from .categories import LANGUAGES, TAG_CATEGORIES, LINK_CATEGORIES


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

    attachment_file = models.ImageField(_('Attachment file'), blank=False)
    content_type    = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id       = models.PositiveIntegerField()
    source_content  = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        """String representation of this model objects."""

        return attachment_file.filename


class Link(models.Model):
    """ Attachment """

    url            = models.URLField(_('URL of the link'), blank=False)
    title          = models.CharField(_('Title of the link'), max_length=200, blank=True)
    category       = models.CharField(_('Category'), max_length=1, default='d', blank=False, choices=LINK_CATEGORIES)
    content_type   = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id      = models.PositiveIntegerField()
    source_content = GenericForeignKey('content_type', 'object_id')
    description    = models.CharField(_('Description'), max_length=256, blank=True, null=True)

    def __str__(self):
        """String representation of this model objects."""

        return self.url


class Tag(models.Model):
    """ Attachment """

    name           = models.CharField(_('Name of the tag'), max_length=200, blank=True, unique=True)
    category       = models.CharField(_('Category of the tag'), choices=TAG_CATEGORIES, max_length=1, blank=False, default='t')
    slug           = models.SlugField(editable=False, blank=True)

    def __str__(self):
        """String representation of this model objects."""

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

    slug                 = models.SlugField(editable=False, blank=True)
    name                 = models.CharField(_('Name'), max_length=200, blank=False, null=True)
    surname              = models.CharField(_('Surname'), max_length=200, blank=True, null=True)
    email                = models.EmailField(_('Email'), blank=True, null=True)
    description          = RichTextUploadingField(_('Description'), blank=True, null=True)

    effective_date       = models.DateField(_('Effective date'), blank=True, null=True,
                                            help_text=_('Date when the content should become available on the public site'))
    expiration_date      = models.DateField(_('Expiration date'), blank=True, null=True,
                                            help_text=_('Date when the content should no longer be visible on the public site'))
    copyright            = models.TextField(_('Copyright'), blank=True, null=True,
                                            help_text=_('A list of copyright info for this content'))
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
    date            = models.DateField(_('Date'), blank=True, null=True)
    slug            = models.SlugField(blank=True, editable=False)
    editorial_title = models.CharField(_('Editorial title'), max_length=200, blank=True, null=True)
    editorial       = RichTextUploadingField(_('Editorial'), blank=True, null=True)
    impressum       = RichTextUploadingField(_('Impressum'), blank=True, null=True)
    links           = GenericRelation(Link)

    # metadata
    effective_date       = models.DateField(_('Effective date'), blank=True, null=True,
                                            help_text=_('Date when the content should become available on the public site'))
    expiration_date      = models.DateField(_('Expiration date'), blank=True, null=True,
                                            help_text=_('Date when the content should no longer be visible on the public site'))
    copyright            = models.TextField(_('Copyright'), blank=True, null=True,
                                            help_text=_('A list of copyright info for this content'))
    comments             = models.TextField(_('Comments'), blank=True, null=True,
                                            help_text=_('Private'))
    is_published         = models.BooleanField(_('Is visible'), default=False, null=False)

    class Meta:
        verbose_name = _('Journal issue')
        verbose_name_plural = _('Journal issues')

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
    issue           = models.ForeignKey(JournalIssue, verbose_name=_('Journal issue'), related_name='texts', blank=True, null=True, on_delete=models.SET_NULL)
    language        = models.CharField(_('Language'), max_length=2, default='en', choices=LANGUAGES)
    date            = models.DateField(_('Date'), blank=True, null=True)
    body            = RichTextUploadingField(_('Body'), blank=True, null=True)
    authors         = models.ManyToManyField(Biography, verbose_name=_('Authors'), related_name='texts_created', blank=True)
    author_text     = models.CharField(_('Author attribution'), max_length=200, null=True)
    translators     = models.ManyToManyField(Biography, verbose_name=_('Translators'), related_name='texts_translated', blank=True)
    translator_text = models.CharField(_('Translation attribution'), max_length=200, blank=True, null=True)
    translations    = models.ManyToManyField('self', blank=True)
    order           = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    column_end      = models.BooleanField(_('End of column'), default=False)

    # metadata
    effective_date       = models.DateField(_('Effective date'), blank=True, null=True,
                                            help_text=_('Date when the content should become available on the public site'))
    expiration_date      = models.DateField(_('Expiration date'), blank=True, null=True,
                                            help_text=_('Date when the content should no longer be visible on the public site'))
    copyright            = models.TextField(_('Copyright'), blank=True, null=True,
                                            help_text=_('A list of copyright info for this content'))
    comments             = models.TextField(_('Comments'), blank=True, null=True,
                                            help_text=_('Private'))
    is_published         = models.BooleanField(_('Is visible'), default=False, null=False)

    class Meta:
        verbose_name = _('Journal text')
        verbose_name_plural = _('Journal texts')
        ordering = ('order',)

    def save(self, *args, **kwargs):
        """Populate automatically 'slug' field"""

        if not self.slug:
            slug = ""
            super(JournalText, self).save(*args, **kwargs)
            if self.authors:
                print(self.id)
                for i,author in enumerate(self.authors.all()):
                    print(author.name)
                    if i>0:
                        slug += "-"
                    if author.surname:
                        slug += slugify(author.surname)
                    else:
                        slug += slugify(author.name)
            else:
                slug = slugify(self.title)
            self.slug = slug
            super(JournalText, self).save(*args, **kwargs)
        else:
            super(JournalText, self).save(*args, **kwargs)

    def get_absolute_url(self):
        # To prevent errors when rendering lists with badly imported text
        # TODO: change this in production
        if self.issue and self.slug and self.language:
            return reverse('journal_text', args=[self.issue.slug, self.slug, self.language])
        else:
            print("El texto " + str(self.pk) + " tiene problemas")
            return None

    def __str__(self):
        """String representation of this model objects."""
        return self.title


class BlogText(models.Model):
    """ Texts of the journals """

    title           = models.CharField(_('Title'), max_length=200, blank=False, null=True)
    slug            = models.SlugField(editable=False, blank=True)
    fulltitle       = models.CharField(_('Full title'), max_length=200, blank=True, null=True)
    subtitle        = models.CharField(_('Subtitle'), max_length=200, blank=True, null=True)
    language        = models.CharField(_('Language'), max_length=2, choices=LANGUAGES)
    date            = models.DateField(_('Date'), blank=True, null=True)
    teaser          = RichTextUploadingField(_('Teaser'), blank=True, null=True)
    body            = RichTextUploadingField(_('Body'), blank=True, null=True)
    authors         = models.ManyToManyField(Biography, verbose_name=_('Authors'),  related_name='blogposts_written', blank=True)
    author_text     = models.CharField(_('Author attribution'), max_length=200, blank=True, null=True)
    translators     = models.ManyToManyField(Biography, verbose_name=_('Translators'), related_name='blogposts_translated', blank=True)
    translator_text = models.CharField(_('Translation attribution'), max_length=200, blank=True, null=True)
    in_home         = models.BooleanField(_('Show in home'), default=False, null=False)
    in_archive      = models.BooleanField(_('Show in archive'), default=False, null=False)
    tags            = models.ManyToManyField(Tag, verbose_name=_('Tags'), related_name='blogposts_tagged', blank=True)

    effective_date       = models.DateField(_('Effective date'), blank=True, null=True,
                                            help_text=_('Date when the content should become available on the public site'))
    expiration_date      = models.DateField(_('Expiration date'), blank=True, null=True,
                                            help_text=_('Date when the content should no longer be visible on the public site'))
    copyright            = models.TextField(_('Copyright'), blank=True, null=True,
                                            help_text=_('A list of copyright info for this content'))
    comments             = models.TextField(_('Comments'), blank=True, null=True,
                                            help_text=_('Private'))
    is_published         = models.BooleanField(_('Is visible'), default=False, null=False)

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

    class Meta:
        verbose_name = _('Blog text')
        verbose_name_plural = _('Blog texts')

    def __str__(self):
        """String representation of this model objects."""
        return self.title

class BlogTextTranslation(models.Model):
    """ Texts of the journals """

    title           = models.CharField(_('Title'), max_length=200, blank=False, null=True)
    slug            = models.SlugField(blank=True, editable=False)
    fulltitle       = models.CharField(_('Full title'), max_length=200, blank=True, null=True)
    subtitle        = models.CharField(_('Subtitle'), max_length=200, blank=True, null=True)
    language        = models.CharField(_('Language'), max_length=2, choices=LANGUAGES)
    source_text     = models.ForeignKey(BlogText, related_name='translations', verbose_name=_('Source text'), on_delete=models.SET_NULL, null=True)
    body            = RichTextUploadingField(_('Body'), blank=True, null=True)
    translator_text = models.CharField(_('Translation attribution'), max_length=200, blank=True, null=True)
    author_text     = models.CharField(_('Author attribution'), max_length=200, blank=True, null=True)
    translators     = models.ManyToManyField(Biography, verbose_name=_('Translators'), blank=True)

    # metadata
    effective_date       = models.DateField(_('Effective date'), blank=True, null=True,
                                            help_text=_('Date when the content should become available on the public site'))
    expiration_date      = models.DateField(_('Expiration date'), blank=True, null=True,
                                            help_text=_('Date when the content should no longer be visible on the public site'))
    copyright            = models.TextField(_('Copyright'), blank=True, null=True,
                                            help_text=_('A list of copyright info for this content'))
    comments             = models.TextField(_('Comments'), blank=True, null=True,
                                            help_text=_('Private'))
    is_published         = models.BooleanField(_('Is visible'), default=False, null=False)

    def save(self, *args, **kwargs):
        """Populate automatically 'slug' field"""
        if not self.slug:
            self.slug = slugify(self.title)

        super(BlogTextTranslation, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Translation')
        verbose_name_plural = _('Translations')

    def __str__(self):
        """String representation of this model objects."""
        return self.title

class Book(models.Model):
    """ Books """

    title              = models.CharField(_('Title'), max_length=200, blank=False, null=True)
    slug               = models.SlugField(editable=False, blank=True)
    date               = models.DateField(_('Date'), blank=True, null=True)
    subtitle           = models.CharField(_('Subtitle'), max_length=200, blank=True, null=True)
    language           = models.CharField(_('Language'), max_length=2, choices=LANGUAGES)
    teaser             = RichTextUploadingField(_('Teaser'), blank=True, null=True)
    body               = RichTextUploadingField(_('Body'), blank=True, null=True)
    authors            = models.ManyToManyField(Biography, verbose_name=_('Authors'), related_name='books_written', blank=True)
    author_text        = models.CharField(_('Author attribution'), max_length=256, blank=False, null=True)
    translators        = models.ManyToManyField(Biography, verbose_name=_('Translators'), related_name='books_translated', blank=True)
    publisher_text     = models.CharField(_('Publisher info'), max_length=200, blank=False, null=True)
    related_books      = models.ManyToManyField('self', verbose_name=_('Related publications'), blank=True)
    in_home            = models.BooleanField(_('Show in home'), default=False, null=False)
    featured_text      = models.TextField(_('Text to be used at featured view in home'), blank=True,
                                            help_text=_('Summary to be shown in the featured view at the home. '
                                                        'In case it\'s empty author attribution will be used instead'))
    in_listings        = models.BooleanField(_('Show in listings'), default=True, null=False)
    pdf_file           = models.FileField(_('Pdf file'), blank=True, null=True)
    epub_file          = models.FileField(_('Epub file'), blank=True, null=True)
    downloads_foot     = models.TextField(_('Text below downloads'), blank=True, max_length=256)
    image              = GenericRelation(Image)
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
    language        = models.CharField(_('Language'), max_length=2, choices=LANGUAGES, default='en')
    teaser          = RichTextUploadingField(_('Teaser'), blank=True, null=True)
    body            = RichTextUploadingField(_('Body'), blank=True, null=True)
    source_text     = models.ForeignKey(Book, related_name='excerpts', verbose_name=_('Source text'), on_delete=models.SET_NULL, null=True)
    is_published    = models.BooleanField(_('Is visible'), default=True, null=False)

    class Meta:
        verbose_name = _('Book excerpt')
        verbose_name_plural = _('Book excerpts')

    def __str__(self):
        """String representation of this model objects."""
        return self.source_text.title + ": " + self.title


class HeaderText(models.Model):

    text     = RichTextUploadingField(_('Text'), blank=False, null=True)
    language = models.CharField(_('Language'), max_length=2, blank=False, choices=LANGUAGES)

    def __str__(self):
        """String representation of this model objects."""
        return self.get_language_display()

class Page(models.Model):

    title    = models.CharField(_('Title'), max_length=200, blank=False, null=True)
    content  = RichTextUploadingField(_('Text'), blank=False, null=True)
    slug     = models.SlugField(_('Slug'), blank=False)

    def get_absolute_url(self):
        return reverse('static_page', args=[self.slug])

    def __str__(self):
        """String representation of this model objects."""
        return self.title

class Event(models.Model):
    """ Events """

    title           = models.CharField(_('Title'), max_length=200, blank=False, null=True)
    slug            = models.SlugField(editable=False, blank=True)
    datetime        = models.DateTimeField(_('Date and time'), blank=False, null=True)
    city            = models.CharField(_('City'), max_length=128, blank=False)
    address         = models.CharField(_('Address'), max_length=256, blank=True)
    body            = RichTextUploadingField(_('Body'), blank=True, null=True)
    summary         = models.TextField(_('Summary'), blank=True, help_text=_('If this field is not empty its content will be used in listings instead of the main body'))
    is_published    = models.BooleanField(_('Is visible'), default=True, null=False)
    in_home         = models.BooleanField(_('Show in home'), default=True, null=False)
    extended_info   = models.BooleanField(_('Read more link'), default=False, null=False,
                                          help_text=_('Check this option if you want the event to have a "Read more" link connected to its section in the listings'))
    links           = GenericRelation(Link)

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


class UserProfile(models.Model):
    """ User profiles """

    user            = models.OneToOneField(User, on_delete=models.CASCADE)
    curated_content = GM2MField()

    @property
    def username(self):
        """Returns full name of user or username"""

        user = self.user
        if user.first_name:
            return user.first_name + " " + user.last_name
        return user.username

    def __str__(self):
        """String representation of this model objects."""

        return self.user.username
