from django.conf import settings
from django.db import models
from django.utils import timezone

from autoslug import AutoSlugField
from imagekit.models import ProcessedImageField


# Create your models here.
class Event(models.Model):
    '''The place where an organiser can create an event'''

    # Event Title
    event_title = models.CharField('Event Title', max_length=256)

    # Event slug
    event_slug = AutoSlugField(populate_from='event_title', default='')

    # Event creation date
    event_date_created = models.DateTimeField(default=timezone.now,
                                        auto_now=False,
                                        auto_now_add=False)

    # Event main image path
    def path_and_rename(instance, filename):
        extension = filename.split('.')[-1]

        return '{}.{}'.format(timezone.now(), extension)

    # Event main image
    event_main_image = ProcessedImageField(upload_to=path_and_rename,
                                           format='jpeg',
                                           options={'quality': 80},)

    # Event organiser
    event_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   related_name='event_user')

    # Return string
    def __str__(self):
        return str(self.event_title)


class EventDateAndTime(models.Model):
    '''The Event organiser can add a date and a time to the event'''

    # The event attached to
    event = models.ForeignKey(
        Event,
        related_name='date_event',
        on_delete=models.CASCADE)

    # The start date and time of the event
    event_start_date = models.DateTimeField(
        'Start Date and Time',
        auto_now=False,
        auto_now_add=False)

    # The end date and time of the event
    event_end_date = models.DateTimeField(
        'End Date and Time',
        auto_now=False,
        auto_now_add=False)
