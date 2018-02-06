from django.test import TestCase

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from .models import Event
from myhub_events.users.models import User


# Create your tests here.
class EventModelTest(TestCase):

    def setUp(self):
        Event.objects.create(
            event_title='My entry title',
            event_slug='my-entry-title',
            event_date_created=timezone.now(),
            event_user=User.objects.create(username='dragos'))

    def test_string_representation(self):
        event = Event.objects.first()
        self.assertEqual(str(event), event.event_title)

    def test_event_title(self):
        event = Event.objects.first()
        self.assertEqual(str(event), event.event_title)

    def test_event_slug(self):
        event = Event.objects.first()
        slug = Event(event_title=event.event_title, event_slug=event.event_title)

        self.assertEqual(str(slug), slug.event_slug)
