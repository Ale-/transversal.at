from django.conf import settings

def loggedin_username_processor(request):
    """Injects into global context texts that populate the slideshow in the header"""

    loggedin_username = request.user.username

    return locals()

def registration_processor(request):
    """Injects into global context texts that populate the slideshow in the header"""

    registration_open = settings.REGISTRATION_OPEN

    return locals()
