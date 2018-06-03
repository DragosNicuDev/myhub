from django.db import models

from events.models import Event, EventInvitee


# Create your models here.
class EventInvitation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    subject = models.CharField(
        max_length=256,
        null=True,
        blank=True
    )

    body = models.TextField(
        null=True,
        blank=True
    )

    to_email = models.ForeignKey(EventInvitee, on_delete=models.CASCADE)

    date_created = models.DateTimeField(auto_now_add=True)

    date_modified = models.DateTimeField(auto_now=True)

    # from_email = models.ForeignKey()

    def __str__(self):
        return str(self.event)
