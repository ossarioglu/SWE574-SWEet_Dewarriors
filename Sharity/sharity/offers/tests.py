from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
import datetime
import pytz

from offers.views import OfferListView, AjaxHandlerView

# Create your tests here.
from .models import Offer
from .forms import OfferSearchForm
from django.contrib.auth.models import User

tz = pytz.timezone('Europe/Istanbul')
now = datetime.datetime.now().replace(tzinfo=tz)

# Create your tests here.
class TestOfferSearchView(TestCase):
    @classmethod
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user_1 = User.objects.create_user(username='TestUser1', password='Test')
        self.user_2 = User.objects.create_user(username='TestUser2', password='Test')
        self.offer_1 = Offer.objects.create(
        owner=self.user_1, 
        title='TestOffer1', 
        start_date=now + datetime.timedelta(hours=2), 
        duration=1, 
        participant_limit=5,
        amendment_deadline=now + datetime.timedelta(hours=1), 
        type=1,
        location='Istanbul, Turkey',
        tags='test',
        )

    def test_offer_search_view(self):
        request = self.factory.get(reverse('offer.list'))
        request.user = self.user_1
        response = OfferListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_offer_search_view_template(self):
        login = self.client.login(username='TestUser1', password='Test')
        response = self.client.get(reverse('offer.list'))
        self.assertTemplateUsed(response, 'offers/offer_list.html')

    def test_offer_search_view_context_form(self):
        request = self.factory.get(reverse('offer.list'))
        request.user = self.user_2
        view = OfferListView()
        view.setup(request)
        view.object_list = view.get_queryset()
        context = view.get_context_data()
        self.assertIn('form', context)

    def test_offer_search_view_context_offers(self):
        request = self.factory.get(reverse('offer.list'))
        request.user = self.user_2
        view = OfferListView()
        view.setup(request)
        view.object_list = view.get_queryset()
        context = view.get_context_data()
        self.assertEqual(len(context['object_list']), 1)

    def test_offer_search_view_ajax(self):
        login = self.client.login(username='TestUser1', password='Test')
        response = self.client.get(reverse('ajax_load_results'), {}, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'offers/ajax_offer_results.html')

    def tearDown(self):
        return super().tearDown()