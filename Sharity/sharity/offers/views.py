from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from .models import Offer
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator
from .forms import OfferCreateForm
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt, csrf_protect


@method_decorator(never_cache, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class OfferCreateView(LoginRequiredMixin, CreateView):
    form_class = OfferCreateForm
    template_name = 'offers/offer_create.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user

        if form.instance.owner != self.request.user:
            return super(OfferCreateView, self).form_invalid(form)
        return super().form_valid(form)

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
