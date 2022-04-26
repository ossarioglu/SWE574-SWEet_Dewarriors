import json

from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView, View
from django.views.generic.edit import FormMixin
from .models import Offer
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator
from .forms import OfferCreateForm, OfferSearchForm
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from tags.services import TagService


@method_decorator(never_cache, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class OfferCreateView(LoginRequiredMixin, CreateView):
    form_class = OfferCreateForm
    template_name = 'offers/offer_create.html'

    def form_invalid(self, form):
        print(form.errors)

    def form_valid(self, form):
        form.instance.owner = self.request.user

        if form.instance.owner != self.request.user:
            return super(OfferCreateView, self).form_invalid(form)

        wb_get_entities_response = TagService.find_by_ids(form.tag_ids)
        claims = []

        if 'entities' in wb_get_entities_response:
            for entity in wb_get_entities_response['entities'].values():
                for claim_id in entity['claims']:
                    if claim_id in ['P31', 'P279']:
                        for claim in entity['claims'][claim_id]:
                            claims.append(claim['mainsnak']['datavalue']['value']['id'])

        form.instance.claims = json.dumps(claims, separators=(',', ':'))

        return super().form_valid(form)

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# @method_decorator(never_cache, name='dispatch')
# @method_decorator(csrf_exempt, name='dispatch')
class OfferDetailView(LoginRequiredMixin, DetailView):
    model = Offer


class AjaxHandlerView(LoginRequiredMixin, View):
    def get(self, request):
        context = {}
        result = Offer.objects.all().exclude(owner=request.user)

        title_query = request.GET.get('title_query')
        location_query = request.GET.get('location_query')
        start_date_query = request.GET.get('start_date_query')
        duration_query = request.GET.get('duration_query')
        tags_query = request.GET.get('tags_query')
        offer_type_query = request.GET.get('type_query')
        owner_query = request.GET.get('owner_query')

        # filter by title
        if title_query:
            result = result.filter(title__icontains=title_query)
        # filter by location
        if location_query:
            result = result.filter(location__icontains=location_query)
        # filter by start date
        if start_date_query:
            result = result.filter(start_date__gt=start_date_query)
        # filter by duration
        if duration_query:
            result = result.filter(duration__lte=duration_query)
        # filter by tags
        if tags_query:
            result = result.filter(tags__icontains=tags_query)
        # filter by type
        if offer_type_query:
            result = result.filter(type=offer_type_query)
        # filter by owner
        if owner_query:
            result = result.filter(owner__username__icontains=owner_query)

        context['filter_flag'] = False
        for key, value in self.request.GET.items():
            if key in ['title_query', 'location_query', 'start_date_query', 'duration_query', 'tags_query',
                       'type_query', 'owner_query'] and value:
                if key == 'type_query':
                    context[key] = list(filter(lambda x: x[0] == int(value), Offer.Type.choices))[0][1]
                else:
                    context[key] = value
                context['filter_flag'] = True

        context['result_list'] = result

        return render(request, 'offers/ajax_offer_results.html', context)


# @method_decorator(never_cache, name='dispatch')
# @method_decorator(csrf_exempt, name='dispatch')
class OfferListView(LoginRequiredMixin, ListView):
    model = Offer
    template_name = 'offers/offer_list.html'

    def get_queryset(self):
        result = Offer.objects.all().exclude(owner=self.request.user)
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = OfferSearchForm()
        context['form'] = form
        return context
