from django.contrib import admin

from .models import Event
# Register your models here.


class EventAdmin(admin.ModelAdmin):
    list_display = (
        'event_title',
        'event_slug',
        'event_user',
        'event_date_created'
    )

admin.site.register(Event, EventAdmin)
