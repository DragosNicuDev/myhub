from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from autoslug import AutoSlugField
from imagekit.models import ProcessedImageField
from localized_fields.models import LocalizedModel
from localized_fields.fields import (LocalizedCharField,
                                     LocalizedFileField,
                                     LocalizedTextField,
                                     LocalizedUniqueSlugField)


# Create your models here.
class Event(LocalizedModel, models.Model):
    '''The place where an organiser can create an event'''

    # Event Title
    # event_title = models.CharField(_('Event Title'), max_length=256)
    event_title = LocalizedCharField(_('Event Title'), max_length=256)

    # Event slug
    # event_slug = AutoSlugField(populate_from='event_title', default='')
    event_slug = LocalizedUniqueSlugField(populate_from='event_title')

    # Event creation date
    event_date_created = models.DateTimeField(default=timezone.now,
                                        auto_now=False,
                                        auto_now_add=False)

    # Event main image path
    def path_and_rename(instance, filename, lang):
        extension = filename.split('.')[-1]

        return '{}-{}.{}'.format(lang, timezone.now(), extension)

    # Event main image
    event_main_image = LocalizedFileField(_('Main image'),
                                           upload_to=path_and_rename,
                                          )

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
        _('Start Date and Time'),
        auto_now=False,
        auto_now_add=False)

    # The end date and time of the event
    event_end_date = models.DateTimeField(
        _('End Date and Time'),
        auto_now=False,
        auto_now_add=False)


class EventDescription(models.Model):
    '''The Event organiser can add a description'''

    # The event attached to
    event = models.ForeignKey(
        Event,
        related_name='event_description',
        on_delete=models.CASCADE
    )

    # Description field
    # event_description = models.TextField()
    event_description = LocalizedTextField(_('Event Description'), null=True, required=False)


class EventLocation(models.Model):
    '''The event location'''

    # The event attached to
    event = models.ForeignKey(
        Event,
        related_name='event_location',
        on_delete=models.CASCADE
    )

    # The event location name
    event_location_name = models.CharField(
        _('Name of the location'),
        max_length=80,
        null=True,
        blank=True
    )

    # The location's address
    event_location_address = models.CharField(
        _('Address of the location'),
        max_length=256,
        null=True,
        blank=True
    )

    # The location date and time (optional)
    event_location_datetime = models.DateTimeField(
        _('Date and Time at the location'),
        help_text=_('This is optional'),
        auto_now=False,
        auto_now_add=False,
        blank=True,
        null=True
    )
