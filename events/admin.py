from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django_summernote.admin import SummernoteModelAdmin

from localized_fields.admin import LocalizedFieldsAdminMixin
from localized_fields.util import get_language_codes
# from ckeditor.widgets import CKEditorWidget

from .models import (
    Event,
    EventDateAndTime,
    EventDescription,
    EventLocation,
    EventInvitee,
    EventFobiForms,
    EventFormEntry)


# class PostAdminForm(forms.ModelForm):
#     event_description = forms.CharField(widget=CKEditorWidget())
#     class Meta:
#         model = EventDescription
#         fields = ('event_description', )
#         # fields = '__all__'
#
# class PostAdmin(admin.ModelAdmin):
#     event_description = forms.CharField(widget=CKEditorWidget())
#     form = PostAdminForm
#     exclude = ('event', )
#
# admin.site.register(EventDescription, PostAdmin)


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


class EventDescAdmin(LocalizedFieldsAdminMixin, admin.TabularInline):
    model = EventDescription
    extra = 0


class EventLocationAdmin(LocalizedFieldsAdminMixin, admin.TabularInline):
    model = EventLocation
    extra = 0


class EventAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = (
        'event_title',
        'slug',
        # 'e_slug',
        'event_user',
        'event_date_created'
    )

    inlines = [
        EventTime,
        EventDescAdmin,
        EventLocationAdmin
    ]


class EventInviteeAdmin(admin.ModelAdmin):
    fields = (
        'event',
        'first_name',
        'last_name',
        'email',
        'token'
    )

    list_display = [f.name for f in EventInvitee._meta.fields]


class EventFobiFormsAdmin(admin.ModelAdmin):
    """FormEntry admin."""

    list_display = (
        'event',
        'name',
        'slug',
        'user',
        'is_public',
        'is_active',
        'created',
        'updated',
        'is_cloneable',
    )
    list_editable = ('is_public', 'is_cloneable')
    list_filter = ('is_public', 'is_cloneable')
    readonly_fields = ('slug',)
    radio_fields = {"user": admin.VERTICAL}
    fieldsets = (
        (_("Form"), {
            'fields': (
                'name',
                'event',
                'is_public',
                'is_cloneable',
                'active_date_from',
                'active_date_to',
                'inactive_page_title',
                'inactive_page_message',
            )
        }),
        (_("Custom"), {
            'classes': ('collapse',),
            'fields': ('success_page_title', 'success_page_message', 'action')
        }),
        # (_("Wizard"), {
        #     'classes': ('collapse',),
        #     'fields': ('form_wizard_entry', 'position',)
        # }),
        (_("User"), {
            'classes': ('collapse',),
            'fields': ('user',)
        }),
        (_('Additional'), {
            'classes': ('collapse',),
            'fields': ('slug',)
        }),
    )
    # inlines = [FormElementEntryInlineAdmin, FormHandlerEntryInlineAdmin]

# class FobiFormWidgetAdmin(admin.ModelAdmin):
#     fields = '__all__'
#
#     list_display = [f.name for f in FobiFormWidget._meta.fields]


admin.site.register(Event, EventAdmin)
admin.site.register(EventInvitee, EventInviteeAdmin)
admin.site.register(EventFormEntry, EventFobiFormsAdmin)
# admin.site.register(EventDescription, SomeModelAdmin)
