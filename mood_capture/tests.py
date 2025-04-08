import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from mood_capture import views
from mood_capture.models import MoodUpload


class MoodTestCase(TestCase):
    def setUp(self) -> None:
        self.user1 = User.objects.create_user('testuser', 'testuser@email.com', '12345')
        self.user2 = User.objects.create_user('testuser2', 'testuser@email.com', '12345')
        self.user1.save()
        self.user2.save()

    def test_capture_mood(self):
        factory = APIRequestFactory()
        req = factory.post('/mood_capture/capture_mood',
                           {"lng": -120, "lat": 37, "mood": "happy"}, format="json")
        force_authenticate(req, user=self.user1)
        self.assertEqual(200, views.capture_mood(req).status_code)

        r = list(MoodUpload.objects.filter(user=self.user1).all())
        r2 = list(MoodUpload.objects.filter(user=self.user2).all())

        self.assertEqual(1, len(r))
        m = r[0]
        self.assertEqual(MoodUpload.Mood.HAPPY.value, m.mood)
        self.assertEqual(-120, m.lng)
        self.assertEqual(37, m.lat)

        self.assertEqual(0, len(r2))

    def test_mood_frequency_distribution(self):
        MoodUpload(user=self.user1, mood=MoodUpload.Mood.HAPPY.value, lat=0, lng=0).save()
        MoodUpload(user=self.user1, mood=MoodUpload.Mood.HAPPY.value, lat=0, lng=0).save()
        MoodUpload(user=self.user1, mood=MoodUpload.Mood.HAPPY.value, lat=0, lng=0).save()

        MoodUpload(user=self.user1, mood=MoodUpload.Mood.NEUTRAL.value, lat=0, lng=0).save()

        MoodUpload(user=self.user1, mood=MoodUpload.Mood.SAD.value, lat=0, lng=0).save()

        MoodUpload(user=self.user2, mood=MoodUpload.Mood.NEUTRAL.value, lat=0, lng=0).save()

        factory = APIRequestFactory()

        req = factory.get('/mood_capture/mood_frequency_distribution', format="json")
        force_authenticate(req, user=self.user1)
        response = views.mood_frequency_distribution(req)
        self.assertEqual(200, response.status_code)
        self.assertEqual({"HAPPY": 3, "NEUTRAL": 1, "SAD": 1}, json.loads(response.content))

        force_authenticate(req, user=self.user2)
        response = views.mood_frequency_distribution(req)
        self.assertEqual(200, response.status_code)
        self.assertEqual({"NEUTRAL": 1}, json.loads(response.content))

    def test_closest_happy_location(self):
        MoodUpload(user=self.user1, mood=MoodUpload.Mood.HAPPY.value, lat=5, lng=6).save()
        MoodUpload(user=self.user1, mood=MoodUpload.Mood.HAPPY.value, lat=100, lng=200).save()
        MoodUpload(user=self.user1, mood=MoodUpload.Mood.HAPPY.value, lat=1, lng=1).save()

        MoodUpload(user=self.user1, mood=MoodUpload.Mood.NEUTRAL.value, lat=0, lng=0).save()

        MoodUpload(user=self.user1, mood=MoodUpload.Mood.SAD.value, lat=0, lng=0).save()

        MoodUpload(user=self.user2, mood=MoodUpload.Mood.NEUTRAL.value, lat=0, lng=0).save()

        factory = APIRequestFactory()

        req = factory.get('/mood_capture/closest_happy_location', {"lat": 1, "lng": 1}, format="json")
        force_authenticate(req, user=self.user1)
        response = views.closest_happy_location(req)
        self.assertEqual(200, response.status_code)
        self.assertEqual({"lat": 1, "lng": 1}, json.loads(response.content))

        force_authenticate(req, user=self.user2)
        response = views.closest_happy_location(req)
        self.assertEqual(200, response.status_code)
        self.assertEqual(None, json.loads(response.content))
