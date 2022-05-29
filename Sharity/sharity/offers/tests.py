from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
import datetime
from django.utils import timezone

from offers.views import OfferListView

# Create your tests here.
from .models import Offer
from member.models import Profile
from django.contrib.auth.models import User

now = timezone.now()

# Create your tests here.
class TestOfferSearchView(TestCase):
    @classmethod
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user_1 = User.objects.create_user(username='TestUser1', password='Test')
        self.user_2 = User.objects.create_user(username='TestUser2', password='Test')
        self.profile_1 = Profile.objects.create(
            user=self.user_1,
            userLocation=r'{"formatted_address":"New York, USA","geometry":{"location":{"lat":43.2994285,"lng":-74.21793260000001},"viewport":{"northeast":{"lat":45.015861,"lng":-71.777491},"southwest":{"lat":40.4773991,"lng":-79.7625901}}},"icon":"https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/geocode-71.png","icon_background_color":"#7B9EB0","icon_mask_base_uri":"https://maps.gstatic.com/mapfiles/place_api/icons/v2/generic_pinlet","name":"New York","photos":[{"height":1440,"html_attributions":["<a href=\"https://maps.google.com/maps/contrib/113288532735585523660\">A Google User</a>"],"photo_reference":"Aap_uEA4Qh1O33AptOUerLhcJdu3KQpvCJEmbZ72S8L4koOWrhy6XSTaYcEd5G3577_XPt1Zavt2U5JxK1J5rgOdft4VennT8VWGjio3jkj8RY15AEY8XUl_K1CvZhR3dejyCPGIFW5aLsVwTN_fjrVRXg4nQ9iRG3WfHtwZuR-DzA-JGPVB","width":1080}],"place_id":"ChIJqaUj8fBLzEwRZ5UY3sHGz90","reference":"ChIJqaUj8fBLzEwRZ5UY3sHGz90","types":["administrative_area_level_1","political"]}',
        )
        self.profile_2 = Profile.objects.create(
            user=self.user_2,
            userLocation=r'{"formatted_address":"New York, USA","geometry":{"location":{"lat":43.2994285,"lng":-74.21793260000001},"viewport":{"northeast":{"lat":45.015861,"lng":-71.777491},"southwest":{"lat":40.4773991,"lng":-79.7625901}}},"icon":"https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/geocode-71.png","icon_background_color":"#7B9EB0","icon_mask_base_uri":"https://maps.gstatic.com/mapfiles/place_api/icons/v2/generic_pinlet","name":"New York","photos":[{"height":1440,"html_attributions":["<a href=\"https://maps.google.com/maps/contrib/113288532735585523660\">A Google User</a>"],"photo_reference":"Aap_uEA4Qh1O33AptOUerLhcJdu3KQpvCJEmbZ72S8L4koOWrhy6XSTaYcEd5G3577_XPt1Zavt2U5JxK1J5rgOdft4VennT8VWGjio3jkj8RY15AEY8XUl_K1CvZhR3dejyCPGIFW5aLsVwTN_fjrVRXg4nQ9iRG3WfHtwZuR-DzA-JGPVB","width":1080}],"place_id":"ChIJqaUj8fBLzEwRZ5UY3sHGz90","reference":"ChIJqaUj8fBLzEwRZ5UY3sHGz90","types":["administrative_area_level_1","political"]}',
        )
        self.offer_1 = Offer.objects.create(
        owner=self.user_1, 
        title='Test', 
        start_date=now + datetime.timedelta(hours=2), 
        duration=1, 
        participant_limit=5,
        amendment_deadline=now + datetime.timedelta(hours=1), 
        type=1,
        location=r'{"formatted_address":"New York, USA","geometry":{"location":{"lat":43.2994285,"lng":-74.21793260000001},"viewport":{"northeast":{"lat":45.015861,"lng":-71.777491},"southwest":{"lat":40.4773991,"lng":-79.7625901}}},"icon":"https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/geocode-71.png","icon_background_color":"#7B9EB0","icon_mask_base_uri":"https://maps.gstatic.com/mapfiles/place_api/icons/v2/generic_pinlet","name":"New York","photos":[{"height":1440,"html_attributions":["<a href=\"https://maps.google.com/maps/contrib/113288532735585523660\">A Google User</a>"],"photo_reference":"Aap_uEA4Qh1O33AptOUerLhcJdu3KQpvCJEmbZ72S8L4koOWrhy6XSTaYcEd5G3577_XPt1Zavt2U5JxK1J5rgOdft4VennT8VWGjio3jkj8RY15AEY8XUl_K1CvZhR3dejyCPGIFW5aLsVwTN_fjrVRXg4nQ9iRG3WfHtwZuR-DzA-JGPVB","width":1080}],"place_id":"ChIJqaUj8fBLzEwRZ5UY3sHGz90","reference":"ChIJqaUj8fBLzEwRZ5UY3sHGz90","types":["administrative_area_level_1","political"]}',
        tags=r'[{"id":"Q4925193","title":"Q4925193","pageid":4706051,"display":{"label":{"value":"lie","language":"en"},"description":{"value":"intentionally false statement to a person or group made by another person or group who knows it is not wholly the truth","language":"en"}},"repository":"wikidata","url":"//www.wikidata.org/wiki/Q4925193","concepturi":"http://www.wikidata.org/entity/Q4925193","label":"lie","description":"intentionally false statement to a person or group made by another person or group who knows it is not wholly the truth","match":{"type":"label","language":"en","text":"lie"}}]',
        )

    def test_offer_search_view_status(self):
        request = self.factory.get(reverse('offer.list'))
        request.user = self.user_1
        response = OfferListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_offer_search_view_template(self):
        login = self.client.login(username='TestUser1', password='Test')
        request = self.client.get(reverse('offer.list'))
        self.assertTemplateUsed(request, 'offers/offer_list.html')

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

    def test_offer_search_view_navbar_search(self):
        request = self.factory.get(reverse('offer.list'), {'title': 'Test'})
        request.user = self.user_2
        view = OfferListView()
        view.setup(request)
        view.object_list = view.get_queryset()
        self.assertEqual(len(view.object_list), 1)

    def test_offer_search_view_ajax_post(self):
        login = self.client.login(username='TestUser2', password='Test')
        response = self.client.post(reverse('ajax_load_results'), data={
            'title': 'Test', 
            'start_date': '',
            'duration': '',
            'tags': '',
            'type': '',
            'owner': '',
            'location': '',
            'distance': '',
            'map-json': '',
            'location-json': '',
            'ljson': ''
        }, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertTemplateUsed(response, 'offers/ajax_offer_results.html')
        self.assertIn('result_list', response.context)
        self.assertEqual(1, len(response.context['result_list']))
        
    def tearDown(self):
        return super().tearDown()