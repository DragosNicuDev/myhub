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

from .utils import create_token
from fobi.models import FormEntry, FormElementEntry


# Create your models here.
class Event(LocalizedModel, models.Model):
    '''The place where an organiser can create an event'''

    # Event Title
    event_title = LocalizedCharField(_('Event Title'), max_length=256)

    # Event slug
    slug = LocalizedUniqueSlugField(populate_from='event_title')

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
    event_location_name = LocalizedCharField(
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


class EventInvitee(models.Model):
    '''Organiser can add invitees'''

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE
    )

    first_name = models.CharField('First Name', max_length=25)

    last_name = models.CharField('Last Name', max_length=15)

    email = models.EmailField(max_length=50)

    token = models.CharField(max_length=15, unique=True, blank=True)

    class Meta:
        unique_together = ('event', 'email')

    def __str__(self):
        return str(self.first_name + ' ' + self.last_name)

    def save(self, *args, **kwargs):
        if self.token is None or self.token == '':
            self.token = create_token(self)
        super().save(*args, **kwargs)


class EventFobiForms(models.Model):
    fobi = models.OneToOneField('fobi.FormEntry')
    event = models.ForeignKey(Event)


class EventFormEntry(FormEntry):
    event = models.ForeignKey(
        Event,
        verbose_name=_("EventFormEntry"),
        on_delete=models.CASCADE
    )


class EventFormElementEntry(FormElementEntry):
    event = models.ForeignKey(
        Event,
        verbose_name=_("EventFormElementEntry"),
        on_delete=models.CASCADE
    )
