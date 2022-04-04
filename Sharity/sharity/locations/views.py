from .services import LocationService


def search(request):
    return LocationService.search(request.GET.get('query'))
