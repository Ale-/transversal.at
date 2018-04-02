from django.conf import settings

def site_info_processor(request):
    """Injects into global context information about the site"""

    html_document_title       = settings.DOCUMENT_TITLE

    return locals()

def debug_processor(request):
    """Injects debug flag into context"""

    debug    = settings.DEBUG
    debug_js = settings.DEBUG_JS

    return locals()
