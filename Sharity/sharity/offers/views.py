import json
from tkinter import E
from tracemalloc import start

from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView, View, FormView
from django.views.generic.edit import FormMixin
from .models import Offer
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator
from .forms import OfferCreateForm, OfferSearchForm
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from tags.services import TagService
from django.http import JsonResponse
from django.db.models import Q


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


class AjaxHandlerView(LoginRequiredMixin, FormView):
    form_class = OfferSearchForm

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
    
    def form_valid(self, form):
        if self.request.is_ajax():
            print(form.cleaned_data)
            context = {}
            filters = {}
            args = Q()
            filter_flag = False
            filter_words = {
                'title': '__icontains',
                'location': '__icontains',
                'start_date': '__gte',
                'duration': '__lte',
                'tags': '__icontains',
                'type': '',
                'owner': '__username__icontains'
            }
            for key, value in form.cleaned_data.items():
                if value != '' and value is not None:
                    filter_flag = True
                    if key == 'tags':
                        context[key + '_query'] = [i.strip() for i in value.split(',') if i.strip() != '']
                        for tag in [i.strip() for i in value.split(',')]:
                            if tag != '':
                                args |= Q(**{key + filter_words[key]: tag})
                    else:
                        context[key + '_query'] = value   
                        filters[key + filter_words[key]] = value

            context['result_list'] = Offer.objects.filter(*(args,), **filters).exclude(owner=self.request.user)
            context['filter_flag'] = filter_flag

            return render(self.request, 'offers/ajax_offer_results.html', context)

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
