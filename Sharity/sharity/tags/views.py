from .services import TagService


def search(request):
    return TagService.search(request.GET.get('query'))


def find_by_id(request, tag_id):
    return TagService.find_by_id(tag_id)


def find_by_ids(request, tag_ids: str):
    return TagService.find_by_ids(tuple(tag_ids.split(',')))
