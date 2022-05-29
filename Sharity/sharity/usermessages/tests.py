from django.test import TestCase, Client, RequestFactory
from django.urls import reverse

# Create your tests here.
from django.contrib.auth.models import User
from member.models import Profile
from .models import UserInbox, UserMessage

from .views import DeletedMessagesView, InboxView, SentMessagesView

class TestUserMessagesView(TestCase):
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
        self.inbox_1 = UserInbox.objects.create(owner=self.profile_1)
        self.inbox_2 = UserInbox.objects.create(owner=self.profile_2)

    def test_main_message_view(self):
        login = self.client.login(username='TestUser1', password='Test')
        response = self.client.get(reverse('usermessages.main'))
        self.assertTemplateUsed(response, 'usermessages/messages_main.html')

    def test_send_message_form(self):
        login = self.client.login(username='TestUser1', password='Test')
        response = self.client.get(reverse('usermessages.create'))
        self.assertTemplateUsed(response, 'usermessages/send_message.html')

    def test_send_message(self):
        login = self.client.login(username='TestUser1', password='Test')
        response = self.client.post(reverse('usermessages.create'),
        data={'to': 'TestUser2', 'subject': 'TestSubject', 'body': 'TestBody'},
        **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertRedirects(response, expected_url='/mail/', status_code=302)

    def test_inbox_view(self):
        login = self.client.login(username='TestUser1', password='Test')
        response = self.client.post(reverse('usermessages.create'),
        data={'to': 'TestUser2', 'subject': 'TestSubject', 'body': 'TestBody'},
        **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.client.logout()

        login = self.client.login(username='TestUser2', password='Test')
        request = self.factory.get(reverse('usermessages.inbox'))
        request.user = self.user_2
        view = InboxView()
        view.setup(request)
        view.object_list = view.get_queryset()
        self.assertEqual(1, len(view.object_list))

    def test_sent_messages_view(self):
        login = self.client.login(username='TestUser1', password='Test')
        response = self.client.post(reverse('usermessages.create'),
        data={'to': 'TestUser2', 'subject': 'TestSubject', 'body': 'TestBody'},
        **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        request = self.factory.get(reverse('usermessages.sent'))
        request.user = self.user_1
        view = SentMessagesView()
        view.setup(request)
        view.object_list = view.get_queryset()
        self.assertEqual(1, len(view.object_list))

    def test_delete_message_view(self):
        login = self.client.login(username='TestUser1', password='Test')
        response = self.client.post(reverse('usermessages.create'),
        data={'to': 'TestUser2', 'subject': 'TestSubject', 'body': 'TestBody'},
        **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        message = UserMessage.objects.first()
        self.client.logout()

        login = self.client.login(username='TestUser2', password='Test')
        response = self.client.post(reverse('usermessages.delete'), 
        data={'id': message.id},
        **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.json()['update'], 'done')

    def test_deleted_messages_view(self):
        login = self.client.login(username='TestUser1', password='Test')
        response = self.client.post(reverse('usermessages.create'),
        data={'to': 'TestUser2', 'subject': 'TestSubject', 'body': 'TestBody'},
        **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.client.logout()

        login = self.client.login(username='TestUser2', password='Test')
        message = UserMessage.objects.first()
        response = self.client.post(reverse('usermessages.delete'), 
        data={'id': message.id},
        **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})

        request = self.factory.get(reverse('usermessages.deleted'))
        request.user = self.user_2
        view = DeletedMessagesView()
        view.setup(request)
        view.object_list = view.get_queryset()
        self.assertEqual(1, len(view.object_list))

    def tearDown(self):
        return super().tearDown()
