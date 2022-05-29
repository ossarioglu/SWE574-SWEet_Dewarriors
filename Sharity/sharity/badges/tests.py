from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
import datetime
from django.utils import timezone

from offers.views import OfferListView

# Create your tests here.
from .models import Offer
from member.models import Profile
from django.contrib.auth.models import User

from unittest.mock import patch

now = timezone.now()

class TestBadgeService(TestCase):
    @classmethod
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user_1 = User.objects.create_user(username='TestUser1', password='Test', date_joined=now)
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

    @patch('badges.signals.profile_detail.send')
    def test_badge_signal_sent_profile_detail(self, mock):
        login = self.client.login(username='TestUser1', password='Test')
        response = self.client.get(reverse('profile', kwargs={'userKey': self.user_1.username}))
        self.assertTrue(mock.called)
        self.assertEqual(mock.call_count, 1)

    @patch('badges.signals.offer_detail.send')
    def test_badge_signal_sent_offer_detail(self, mock):
        login = self.client.login(username='TestUser1', password='Test')
        response = self.client.get(reverse('offers.detail', kwargs={'pk': self.offer_1.pk}))
        self.assertTrue(mock.called)
        self.assertEqual(mock.call_count, 1)

    @patch('badges.signals.timeline.send')
    def test_badge_signal_sent_timeline(self, mock):
        login = self.client.login(username='TestUser1', password='Test')
        response = self.client.get(reverse('offer.list'))
        self.assertTrue(mock.called)
        self.assertEqual(mock.call_count, 1)

    def tearDown(self):
        return super().tearDown()