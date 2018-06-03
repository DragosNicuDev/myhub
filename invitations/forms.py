from django import forms

from .models import EventInvitation


class EventInvitationForm(forms.ModelForm):
    class Meta:
        model = EventInvitation
        fields = ['event', 'subject', 'body', 'to_email']
