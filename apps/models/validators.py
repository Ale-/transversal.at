# python
import os
import magic
# django
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class FileTypeValidator(object):

    def __init__(self, mime_types=[
        "application/pdf",
        "application/msword",
        "application/vnd.oasis.opendocument.text",
        "application/vnd.ms-excel",
        "application/vnd.oasis.opendocument.spreadsheet",
        "plain/text",
        ]):
        self.mime_types = mime_types
        self.type_error = r"El archivo '%(name)s' tiene formato %(format)s. Revise arriba los formatos permitidos"

    def __call__(self, value):
        try:
            mime = magic.from_buffer(value.read(), mime=True)
            print(mime)
            if mime not in self.mime_types:
                raise ValidationError(_(self.type_error) % { 'name' : value.name, 'format' : mime.split('/')[1] })
        except ValueError:
            pass
