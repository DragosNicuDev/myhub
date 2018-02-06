from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from .models import (
    Event,
    EventDateAndTime,
    EventDescription,
    EventLocation)


# Apply summernote to all TextField in model.
class SomeModelAdmin(SummernoteModelAdmin):  # instead of ModelAdmin
    summer_note_fields = '__all__'


class EventTime(admin.TabularInline):
    model = EventDateAndTime
    extra = 0


class EventDescAdmin(admin.TabularInline):
    model = EventDescription
    extra = 0


class EventLocationAdmin(admin.TabularInline):
    model = EventLocation
    extra = 0


class EventAdmin(admin.ModelAdmin):
    list_display = (
        'event_title',
        'event_slug',
        'event_user',
        'event_date_created'
    )

    inlines = [
        EventTime,
        EventDescAdmin,
        EventLocationAdmin
    ]

admin.site.register(Event, EventAdmin)
admin.site.register(EventDescription, SomeModelAdmin)
