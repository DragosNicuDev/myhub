from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from localized_fields.admin import LocalizedFieldsAdminMixin

from .models import (
    Event,
    EventDateAndTime,
    EventDescription,
    EventLocation)


# Apply summernote to all TextField in model.
# class SomeModelAdmin(SummernoteModelAdmin):  # instead of ModelAdmin
class SomeModelAdmin(LocalizedFieldsAdminMixin, SummernoteModelAdmin):  # instead of ModelAdmin
    # summer_note_fields = '__all__'
    # summer_note_fields = 'event_description'
    # summer_note_fields = 'event_trans'
    pass


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
