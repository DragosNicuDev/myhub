from django.conf import settings
from django.views.generic import DetailView, ListView, TemplateView

# Create your views here.
from .models import (
    Event,
    EventDateAndTime,
    EventDescription,
    EventLocation)


class EventTemplateView(TemplateView):
    model = Event
    template_name = 'events/event_detail.html'

    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['event'] = Event.objects.first()
       context['date_time'] = EventDateAndTime.objects.first()
       context['description'] = EventDescription.objects.first()
       context['gmap_key'] = settings.EASY_MAPS_GOOGLE_MAPS_API_KEY
       context['location'] = EventLocation.objects.all()
       return context
