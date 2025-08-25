from django.http import HttpResponse

def health_check(request):
    """A simple view that returns a 200 OK response."""
    return HttpResponse("OK")