from django import forms

from .models import EventInvitation


class EventInvitationForm(forms.ModelForm):
    class Meta:
        model = EventInvitation
        fields = ['event', 'subject_en', 'subject_ro', 'body', 'to_email']
