import json

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

from badges.signals import offer_detail, timeline
from badges.models import *
from django.utils import timezone

from member.models import Profile
from .utils import distance, get_lat, get_long, order_offers
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

    def dispatch(self, request, *args, **kwargs):
        offer = self.get_object()
        offer_detail.send(sender=self.__class__, owner_pk=[offer.owner.pk])
        return super().dispatch(request, *args, **kwargs)

class AjaxHandlerView(LoginRequiredMixin, FormMixin, ListView):
    form_class = OfferSearchForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
    
    def form_valid(self, form):
        if self.request.is_ajax():
            context = {}
            filters = {}
            tag_args = Q()
            title_args = Q()
            location_args = Q()
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

            # get search parameter -> distance
            d = form.cleaned_data.pop('distance')
            # get search parameter -> location
            ljson = form.cleaned_data.pop('location-json')

            for key, value in form.cleaned_data.items():
                if value != '' and value != '[]' and value is not None:
                    filter_flag = True
                    if key == 'tags':
                        context[key + '_query'] = [i.strip() for i in value.split(',') if i.strip() != '']
                        for tag in [i.strip() for i in value.split(',') if i.strip() != '']:
                            tag_args |= Q(**{key + filter_words[key]: tag})
                    elif key == 'title':
                        context[key + '_query'] = value
                        for tag in [i.strip() for i in value.split(' ') if i.strip() != '']:
                            title_args |= Q(**{key + filter_words[key]: tag})
                    elif key == 'location':
                        context[key + '_query'] = value
                        for tag in [i.strip() for i in value.split(' ') if i.strip() != '']:
                            location_args |= Q(**{key + filter_words[key]: tag})
                    else:
                        if key == 'type':
                            context[key + '_query'] = 'Service' if value == 1 else 'Event'
                        else:
                            context[key + '_query'] = value  
                        filters[key + filter_words[key]] = value

            # if only location
            if ljson == '' and d is None:
                arguments = tag_args & title_args & location_args
            else:
                arguments = (tag_args & title_args) | location_args

            qs = Offer.objects.filter(*(arguments, ), **filters).exclude(owner=self.request.user).exclude(end_date__lt=timezone.now())

            ### handle location-json and distance filters last ###
            # if location-json and distance queries are present
            if d is not None and ljson != '':
                filter_flag = True
                # get desired location
                profile_loc = (get_lat(ljson), get_long(ljson))
                qs = [i for i in qs if distance(profile_loc[0], i.get_latitude(), profile_loc[1], i.get_longitude()) <= d]
                context['distance_query'] = d
                if 'location_query' not in context.keys():
                    context['location_query'] = json.loads(str(ljson).replace("\\'", '"')).get('formatted_address')
            # else if only distance query is present
            elif d is not None and ljson == '':
                filter_flag = True
                # get desired location
                profile = Profile.objects.get(user=self.request.user)
                profile_loc = (profile.get_latitude(), profile.get_longitude())
                qs = [i for i in qs if distance(profile_loc[0], i.get_latitude(), profile_loc[1], i.get_longitude()) <= d]
                context['distance_query'] = d
            # else if only location-json query is present
            elif d is None and ljson != '':
                filter_flag = True
                # get desired location
                profile_loc = (get_lat(ljson), get_long(ljson))
                qs = [i for i in qs if distance(profile_loc[0], i.get_latitude(), profile_loc[1], i.get_longitude()) <= 300]
                if 'location_query' not in context.keys():
                    context['location_query'] = json.loads(str(ljson).replace("\\'", '"')).get('formatted_address')

            context['result_list'] = order_offers(qs)
            context['filter_flag'] = filter_flag

            owners = [offer.owner.pk for offer in qs]
            timeline.send(sender=self.__class__, owner_pk=owners)

            return render(self.request, 'offers/ajax_offer_results.html', context)

class OfferListView(LoginRequiredMixin, ListView):
    model = Offer
    template_name = 'offers/offer_list.html'

    def dispatch(self, request, *args, **kwargs):
        owners = [offer.owner.pk for offer in self.get_queryset()]
        timeline.send(sender=self.__class__, owner_pk=owners)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.GET.get('title'):
            args = Q()
            for keyword in [i.strip() for i in self.request.GET.get('title').split(' ') if i.strip() != '']:
                args |= Q(**{'title__icontains': keyword})
            result = Offer.objects.filter(*(args,)).exclude(owner=self.request.user).exclude(end_date__lt=timezone.now())
        else:
            result = Offer.objects.all().exclude(owner=self.request.user).exclude(end_date__lt=timezone.now())
        return order_offers(result)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = OfferSearchForm()
        context['form'] = form
        if self.request.GET.get('title'):
            context['title_query'] = self.request.GET.get('title')
        return context
