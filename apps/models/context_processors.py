# django
from django.conf import settings
# project
from . import models

def slideshow_header_processor(request):
    """Injects into global context texts that populate the slideshow in the header"""

    slideshow_header_texts = models.HeaderText.objects.all()

    return locals()

def slideshow_header_processor(request):
    """Injects into global context texts that populate the slideshow in the header"""

    slideshow_header_texts = models.HeaderText.objects.all()

    return locals()
