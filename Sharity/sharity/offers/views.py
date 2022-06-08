import json

from django.shortcuts import redirect, render
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView, View, FormView
from django.views.generic.edit import FormMixin
from .models import Offer
from apply.models import Application
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator
from .forms import OfferCreateForm, OfferForm, OfferSearchForm
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from tags.services import TagService
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from decouple import config
from django.shortcuts import render
from functools import reduce
import operator

from badges.signals import offer_detail, timeline
from badges.models import *
from django.utils import timezone
from datetime import datetime


from member.models import Profile
from .utils import distance, get_lat, get_long, order_offers


@method_decorator(never_cache, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class OfferCreateView(LoginRequiredMixin, CreateView):
    form_class = OfferCreateForm
    template_name = 'offers/offer_create.html'

    def form_invalid(self, form):
        print(len(form.errors), "------ THESE ARE ERRORS ----")

        return super().form_invalid(form)

    def form_valid(self, form):
        try:
            form.instance.owner = self.request.user

            if form.instance.owner != self.request.user:
                return super(OfferCreateView, self).form_invalid(form)

            wb_get_entities_response = TagService.find_by_ids(form.tag_ids)
            claims = []

            if 'entities' in wb_get_entities_response:
                for entity_id in wb_get_entities_response['entities']:
                    for claim_id in wb_get_entities_response['entities'][entity_id]['claims']:
                        if claim_id in ['P31', 'P279', 'P361', 'P366', 'P5008', 'P5125', 'P1343', 'P3095', 'P61', 'P495', 'P1424', 'P1441']:
                            for claim in wb_get_entities_response['entities'][entity_id]['claims'][claim_id]:
                                claims.append(claim['mainsnak']['datavalue']['value']['id'])
                    claims.append(entity_id)

            form.instance.claims = json.dumps(claims, separators=(',', ':'))

            return super().form_valid(form)
        except AttributeError:
            print("This is an attribute erroooooooor!!!")
            return super(OfferCreateView, self).form_invalid(form)

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
    
    def get_object(self):
        offer = Offer.objects.get(uuid=self.kwargs.get('pk'))
        return offer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        offer = self.get_object()
        application = Application.objects.filter(serviceID=offer).filter(requesterID=self.request.user)

        context['applications'] = application

        
        return context


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
            keyword_args = Q()
            location_args = Q()
            filter_flag = False
            filter_words = {
                'keyword': '__icontains',
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
                    elif key == 'keyword':
                        context[key + '_query'] = value
                        for word in [i.strip() for i in value.split(' ') if i.strip() != '']:
                            keyword_args |= Q(**{'title' + filter_words[key]: word})
                            keyword_args |= Q(**{'description' + filter_words[key]: word})
                    elif key == 'location':
                        context[key + '_query'] = value
                        for loc in [i.strip() for i in value.split(' ') if i.strip() != '']:
                            location_args |= Q(**{key + filter_words[key]: loc})
                    else:
                        if key == 'type':
                            context[key + '_query'] = 'Service' if value == 1 else 'Event'
                        else:
                            context[key + '_query'] = value  
                        filters[key + filter_words[key]] = value

            # if only location
            if ljson == '' and d is None:
                arguments = tag_args & keyword_args & location_args
            else:
                arguments = (tag_args & keyword_args) | location_args
            print(arguments)

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
                try:
                    profile_loc = (profile.get_latitude(), profile.get_longitude())
                    qs = [i for i in qs if distance(profile_loc[0], i.get_latitude(), profile_loc[1], i.get_longitude()) <= d]
                    context['distance_query'] = d
                except json.JSONDecodeError:
                    form.add_error('__all__', 'Profile has no location.')
                    return self.form_invalid(form)
            # else if only location-json query is present
            elif d is None and ljson != '':
                filter_flag = True
                # get desired location
                profile_loc = (get_lat(ljson), get_long(ljson))
                qs = [i for i in qs if distance(profile_loc[0], i.get_latitude(), profile_loc[1], i.get_longitude()) <= 300]
                if 'location_query' not in context.keys():
                    context['location_query'] = json.loads(str(ljson).replace("\\'", '"')).get('formatted_address')

            context['result_list'] = order_offers(qs, self.request.user)
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
        return order_offers(result, self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = OfferSearchForm()
        context['form'] = form
        if self.request.GET.get('title'):
            context['title_query'] = self.request.GET.get('title')
        return context


def deleteOffer(request, sID):
    
    offer = Offer.objects.get(uuid=sID)
    
    if request.user != offer.owner:
        return HttpResponse('You are not allowed to delete this offer')
    
    #If confirmation from user is posted, record for service is deleted.
    if request.method == 'POST':
        offer.delete()
        return redirect('home')
    return render(request, 'offers/delete.html', {'obj':offer})


def updateOffer(request, sID):

    # Information for requested service is retreived from database, and added to Form
    offer = Offer.objects.get(uuid=sID)

    if request.user != offer.owner:
        return HttpResponse('You are not allowed to update this offer')

    # When user posts information from Form, relevant fields are matched with object, and service is saved.
    if request.method == 'POST':
        form = OfferForm(request.POST)    
        offer.title = request.POST.get('title')
        offer.description = request.POST.get('description')
        offer.location = request.POST.get('location-json')
        offer.tags = request.POST.get('tags-json')
        offer.start_date = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d %H:%M')
        offer.duration = int(request.POST.get('duration'))
        offer.end_date = request.POST.get('end_date')
        offer.participant_limit = request.POST.get('participant_limit')
        offer.amendment_deadline = datetime.strptime(request.POST.get('amendment_deadline'), '%Y-%m-%d %H:%M') 
        offer.type = request.POST.get('type')
        if request.FILES.get('photo') is not None:
            offer.picture = request.FILES.get('photo')
        offer.save()
        return redirect('home')

    else:
        form = OfferForm(instance=offer)    

    context = {'form':form, 'offer':offer}
    return render(request, 'offers/update_offer.html', context)

