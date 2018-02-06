from django.contrib import admin

from .models import (
    Event,
    EventDateAndTime,
    EventDescription)
# Register your models here.


class EventTime(admin.TabularInline):
    model = EventDateAndTime
    extra = 0


class EventDescAdmin(admin.TabularInline):
    model = EventDescription
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
        EventDescAdmin
    ]

admin.site.register(Event, EventAdmin)
