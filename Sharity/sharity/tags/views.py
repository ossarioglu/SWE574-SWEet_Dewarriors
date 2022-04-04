from .services import TagService


def search(request):
    return TagService.search(request.GET.get('query'))
