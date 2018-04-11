# django #
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.urls import reverse
# contrib
from ckeditor_uploader.fields import RichTextUploadingField
# project
from .categories import LANGUAGES


class Image(models.Model):
    """ Image """

    image_file     = models.ImageField(_('Image file'), blank=False)
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
    content_type   = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id      = models.PositiveIntegerField()
    source_content = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        """String representation of this model objects."""

        return self.url


class Metadata(models.Model):
    """ Metadata of the different content items """

    effective_date       = models.DateField(_('Effective date'), blank=True, null=True,
                                            help_text=_('Date when the content should become available on the public site'))
    expiration_date      = models.DateField(_('Expiration date'), blank=True, null=True,
                                            help_text=_('Date when the content should no longer be visible on the public site'))
    content_author       = models.TextField(_('Creators'), blank=True, null=True,
                                            help_text=_('Persons responsible for creating the content of this item. The principal creator should come first.'))
    content_contributors = models.TextField(_('Contributors'), blank=True, null=True,
                                            help_text=_('Persons responsible for making contributions to the content of this item.'))
    copyright            = models.TextField(_('Copyright'), blank=True, null=True,
                                            help_text=_('A list of copyright info for this content'))
    comments             = models.TextField(_('Comments'), blank=True, null=True,
                                            help_text=_('Private'))
    is_published         = models.BooleanField(_('Is visible'), default=False, null=False)
    content_type         = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id            = models.PositiveIntegerField()
    source_content       = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('Metadata')
        verbose_name_plural = _('Metadata')
        unique_together   = ('content_type', 'object_id')

    def __str__(self):
        """String representation of this model objects."""

        return str(self.source_content)


class Biography(models.Model):
    """ Biographies of people that collaborate or work in the different texts """

    slug                 = models.SlugField(editable=False, blank=True)
    name                 = models.CharField(_('Name'), max_length=200, blank=False, null=True)
    surname              = models.CharField(_('Surname'), max_length=200, blank=True, null=True)
    email                = models.EmailField(_('Email'), blank=True, null=True)
    description          = RichTextUploadingField(_('Description'), blank=True, null=True)
    metadata             = GenericRelation(Metadata)

    effective_date       = models.DateField(_('Effective date'), blank=True, null=True,
                                            help_text=_('Date when the content should become available on the public site'))
    expiration_date      = models.DateField(_('Expiration date'), blank=True, null=True,
                                            help_text=_('Date when the content should no longer be visible on the public site'))
    content_author       = models.TextField(_('Creators'), blank=True, null=True,
                                            help_text=_('Persons responsible for creating the content of this item. The principal creator should come first.'))
    content_contributors = models.TextField(_('Contributors'), blank=True, null=True,
                                            help_text=_('Persons responsible for making contributions to the content of this item.'))
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
    metadata        = GenericRelation(Metadata)

    # metadata
    effective_date       = models.DateField(_('Effective date'), blank=True, null=True,
                                            help_text=_('Date when the content should become available on the public site'))
    expiration_date      = models.DateField(_('Expiration date'), blank=True, null=True,
                                            help_text=_('Date when the content should no longer be visible on the public site'))
    content_author       = models.TextField(_('Creators'), blank=True, null=True,
                                            help_text=_('Persons responsible for creating the content of this item. The principal creator should come first.'))
    content_contributors = models.TextField(_('Contributors'), blank=True, null=True,
                                            help_text=_('Persons responsible for making contributions to the content of this item.'))
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

    # def save(self, *args, **kwargs):
    #     """Populate automatically 'slug' field"""
    #     if not self.slug:
    #         self.slug = self.date.strftime("%m%y")

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


class JournalText(models.Model):
    """ Texts of the journals """

    title           = models.CharField(_('Title'), max_length=200, blank=False, null=True)
    slug            = models.SlugField(blank=True)
    fulltitle       = models.CharField(_('Full title'), max_length=200, blank=True, null=True)
    subtitle        = models.CharField(_('Subtitle'), max_length=200, blank=True, null=True)
    issue           = models.ForeignKey(JournalIssue, verbose_name=_('Journal issue'), related_name='texts', blank=True, null=True, on_delete=models.SET_NULL)
    language        = models.CharField(_('Language'), max_length=2, default='en', choices=LANGUAGES)
    date            = models.DateTimeField(_('Date'), blank=True, null=True)
    body            = RichTextUploadingField(_('Body'), blank=True, null=True)
    authors         = models.ManyToManyField(Biography, verbose_name=_('Authors'), related_name='texts_created', blank=True)
    author_text     = models.CharField(_('Author attribution'), max_length=200, blank=False, null=True)
    translators     = models.ManyToManyField(Biography, verbose_name=_('Translators'), related_name='texts_translated', blank=True)
    translator_text = models.CharField(_('Translation attribution'), max_length=200, blank=True, null=True)
    translations    = models.ManyToManyField('self', blank=True)

    # metadata
    effective_date       = models.DateField(_('Effective date'), blank=True, null=True,
                                            help_text=_('Date when the content should become available on the public site'))
    expiration_date      = models.DateField(_('Expiration date'), blank=True, null=True,
                                            help_text=_('Date when the content should no longer be visible on the public site'))
    content_author       = models.TextField(_('Creators'), blank=True, null=True,
                                            help_text=_('Persons responsible for creating the content of this item. The principal creator should come first.'))
    content_contributors = models.TextField(_('Contributors'), blank=True, null=True,
                                            help_text=_('Persons responsible for making contributions to the content of this item.'))
    copyright            = models.TextField(_('Copyright'), blank=True, null=True,
                                            help_text=_('A list of copyright info for this content'))
    comments             = models.TextField(_('Comments'), blank=True, null=True,
                                            help_text=_('Private'))
    is_published         = models.BooleanField(_('Is visible'), default=False, null=False)

    class Meta:
        verbose_name = _('Journal text')
        verbose_name_plural = _('Journal texts')
        ordering = ('title',)

    def save(self, *args, **kwargs):
        """Populate automatically 'slug' field"""
        if not self.slug:
            slug = ""
            if self.authors:
                for i,author in enumerate(self.authors.all()):
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

    def get_absolute_url(self):
        return reverse('journal_text', args=[self.issue.slug, self.slug])

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
    metadata        = GenericRelation(Metadata)

    effective_date       = models.DateField(_('Effective date'), blank=True, null=True,
                                            help_text=_('Date when the content should become available on the public site'))
    expiration_date      = models.DateField(_('Expiration date'), blank=True, null=True,
                                            help_text=_('Date when the content should no longer be visible on the public site'))
    content_author       = models.TextField(_('Creators'), blank=True, null=True,
                                            help_text=_('Persons responsible for creating the content of this item. The principal creator should come first.'))
    content_contributors = models.TextField(_('Contributors'), blank=True, null=True,
                                            help_text=_('Persons responsible for making contributions to the content of this item.'))
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
        return reverse('blog_text', args=[self.slug])

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
    metadata        = GenericRelation(Metadata)

    # metadata
    effective_date       = models.DateField(_('Effective date'), blank=True, null=True,
                                            help_text=_('Date when the content should become available on the public site'))
    expiration_date      = models.DateField(_('Expiration date'), blank=True, null=True,
                                            help_text=_('Date when the content should no longer be visible on the public site'))
    content_author       = models.TextField(_('Creators'), blank=True, null=True,
                                            help_text=_('Persons responsible for creating the content of this item. The principal creator should come first.'))
    content_contributors = models.TextField(_('Contributors'), blank=True, null=True,
                                            help_text=_('Persons responsible for making contributions to the content of this item.'))
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

    title           = models.CharField(_('Title'), max_length=200, blank=False, null=True)
    slug            = models.SlugField(editable=False, blank=True)
    date            = models.DateField(_('Date'), blank=True, null=True)
    subtitle        = models.CharField(_('Subtitle'), max_length=200, blank=True, null=True)
    language        = models.CharField(_('Language'), max_length=2, choices=LANGUAGES)
    teaser          = RichTextUploadingField(_('Teaser'), blank=True, null=True)
    body            = RichTextUploadingField(_('Body'), blank=True, null=True)
    authors         = models.ManyToManyField(Biography, verbose_name=_('Authors'), related_name='books_written', blank=True)
    author_text     = models.CharField(_('Author attribution'), max_length=200, blank=False, null=True)
    translators     = models.ManyToManyField(Biography, verbose_name=_('Translators'), related_name='books_translated', blank=True)
    publisher_text  = models.CharField(_('Publisher info'), max_length=200, blank=False, null=True)
    related_books   = models.ManyToManyField('self', verbose_name=_('Related publications'), blank=True)
    in_home         = models.BooleanField(_('Show in home'), default=False, null=False)
    in_listings     = models.BooleanField(_('Show in listings'), default=True, null=False)
    pdf_file        = models.FileField(_('Pdf file'), blank=True, null=True)
    epub_file       = models.FileField(_('Epub file'), blank=True, null=True)
    metadata        = GenericRelation(Metadata)
    image           = GenericRelation(Image)

    effective_date       = models.DateField(_('Effective date'), blank=True, null=True,
                                            help_text=_('Date when the content should become available on the public site'))
    expiration_date      = models.DateField(_('Expiration date'), blank=True, null=True,
                                            help_text=_('Date when the content should no longer be visible on the public site'))
    content_author       = models.TextField(_('Creators'), blank=True, null=True,
                                            help_text=_('Persons responsible for creating the content of this item. The principal creator should come first.'))
    content_contributors = models.TextField(_('Contributors'), blank=True, null=True,
                                            help_text=_('Persons responsible for making contributions to the content of this item.'))
    copyright            = models.TextField(_('Copyright'), blank=True, null=True,
                                            help_text=_('A list of copyright info for this content'))
    comments             = models.TextField(_('Comments'), blank=True, null=True,
                                            help_text=_('Private'))
    is_published         = models.BooleanField(_('Is visible'), default=False, null=False)

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
