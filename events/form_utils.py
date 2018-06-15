import datetime

from django.contrib import messages
from django.core import validators
from django.http import Http404

from dragos_content_text.widget import DragosNoneWidget

from django.forms.fields import CharField, ChoiceField, Field, MultipleChoiceField
from django.forms.models import ModelChoiceField

from .models import Event, EventFormEntry

from fobi.base import (
    form_element_plugin_registry,
    form_handler_plugin_registry,
)

from fobi.models import (
    FormElement,
    FormElementEntry,
    FormHandler,
    FormHandlerEntry,
    FormWizardHandler
    )


class DragosNoneField(Field):
    widget = DragosNoneWidget

    def __init__(self, required=True, widget=None, label=None, initial=None,
                 conditional=None, conditioned_data=None, is_conditioned=None,
                 help_text='', error_messages=None, show_hidden_initial=False,
                 validators=(), localize=False, disabled=False, label_suffix=None):
        super().__init__(
            required=required, widget=widget, label=label, initial=initial,
            help_text=help_text)
        self.conditional = conditional
        self.is_conditioned = is_conditioned
        self.conditioned_data = conditioned_data



class DragosChoiceField(ChoiceField):
    def __init__(self, conditional=None, conditioned_data=None,
                is_conditioned=None, conditioned_by=None, required=True, choices=None,
                 ro_choices=None, widget=None, label=None, ro_label=None,
                 initial=None, help_text='', *args, **kwargs):
        super(DragosChoiceField, self).__init__(
            required=required, widget=widget, label=label, initial=initial,
            help_text=help_text, choices=choices, *args, **kwargs
        )
        self.ro_label = ro_label
        self.choices = choices
        self.ro_choices = ro_choices
        self.conditional = conditional
        self.is_conditioned = is_conditioned
        self.conditioned_data = conditioned_data
        self.conditioned_by = conditioned_by


class DragosMultipleChoiceField(MultipleChoiceField):
    def __init__(self, conditional=None, conditioned_data=None,
                is_conditioned=None, required=True, choices=None, ro_choices=None,
                 widget=None, label=None, ro_label=None, initial=None, help_text='',
                 *args, **kwargs):
        super(DragosMultipleChoiceField, self).__init__(
            required=required, widget=widget, label=label, initial=initial,
            help_text=help_text, choices=choices, *args, **kwargs
        )
        self.ro_label = ro_label
        self.choices = choices
        self.ro_choices = ro_choices
        self.conditional = conditional
        self.is_conditioned = is_conditioned
        self.conditioned_data = conditioned_data


class DragosCharField(CharField):
    def __init__(self, max_length=None, min_length=None, strip=True,
                 empty_value='', conditional=None, conditioned_data=None,
                 is_conditioned=None, ro_label=None,
                 *args, **kwargs):
        self.max_length = max_length
        self.min_length = min_length
        self.strip = strip
        self.empty_value = empty_value
        self.conditional = conditional
        self.is_conditioned = is_conditioned
        self.conditioned_data = conditioned_data
        # self.en_label = en_label
        self.ro_label = ro_label

        super(DragosCharField, self).__init__(*args, **kwargs)
        if min_length is not None:
            self.validators.append(validators.MinLengthValidator(int(min_length)))
        if max_length is not None:
            self.validators.append(validators.MaxLengthValidator(int(max_length)))


def get_select_field_cond_data(raw_cond_data,
                             key_type=None,
                             value_type=None,
                             fail_silently=True):
    """Get select field choices.

    Used in ``radio``, ``select`` and other choice based
    fields.

    :param str raw_cond_data:
    :param type key_type:
    :param type value_type:
    :param bool fail_silently:
    :return list:
    """
    cond_data = []  # Holds return value
    keys = set([])  # For checking uniqueness of keys
    values = set([])  # For checking uniqueness of values

    # Looping through the raw data
    for cond in raw_cond_data.split('\n'):
        cond = cond.strip()
        # If comma separated key, value
        if ',' in cond:
            key, value = cond.split(',', 1)
            key = key.strip()

            # If type specified, cast to the type
            if key_type and key is not None:
                try:
                    key = key_type(key)
                except (ValueError, TypeError):
                    return [] if fail_silently else None

            value = value.strip()
            # If type specified, cast to the type
            if value_type and value is not None:
                try:
                    value = value_type(value)
                except (ValueError, TypeError):
                    return [] if fail_silently else None

            if key is not None \
                    and key not in keys \
                    and value not in values:
                cond_data.append((key, value))
                keys.add(key)
                values.add(value)

        # If key is also the value
        else:
            cond = cond.strip()
            if cond is not None \
                    and cond not in keys \
                    and cond not in values:
                cond_data.append(cond)
                keys.add(cond)
                values.add(cond)

    return cond_data

def prepare_form_entry_export_data(form_entry,
                                   form_element_entries=None,
                                   form_handler_entries=None):
    """Prepare form entry export data.

    :param fobi.modes.FormEntry form_entry: Instance of.
    :param django.db.models.QuerySet form_element_entries: QuerySet of
        FormElementEntry instances.
    :param django.db.models.QuerySet form_handler_entries: QuerySet of
        FormHandlerEntry instances.
    :return str:
    """
    data = {
        'name': form_entry.name,
        'event': form_entry.event.id,
        'slug': form_entry.slug,
        'is_public': False,
        'is_cloneable': False,
        # 'position': form_entry.position,
        'success_page_title': form_entry.success_page_title,
        'success_page_message': form_entry.success_page_message,
        'action': form_entry.action,
        'form_elements': [],
        'form_handlers': [],
    }

    if not form_element_entries:
        form_element_entries = form_entry.formelemententry_set.all()[:]

    if not form_handler_entries:
        form_handler_entries = form_entry.formhandlerentry_set.all()[:]

    for form_element_entry in form_element_entries:
        data['form_elements'].append(
            {
                'plugin_uid': form_element_entry.plugin_uid,
                'position': form_element_entry.position,
                'plugin_data': form_element_entry.plugin_data,
            }
        )

    for form_handler_entry in form_handler_entries:
        data['form_handlers'].append(
            {
                'plugin_uid': form_handler_entry.plugin_uid,
                'plugin_data': form_handler_entry.plugin_data,
            }
        )
    return data


def perform_form_entry_import(request, form_data):
    """Perform form entry import.

    :param django.http.HttpRequest request:
    :param dict form_data:
    :return :class:`fobi.modes.FormEntry: Instance of.
    """
    form_elements_data = form_data.pop('form_elements', [])
    form_handlers_data = form_data.pop('form_handlers', [])

    form_data_keys_whitelist = (
        'name',
        'event',
        'title',
        'slug',
        'is_public',
        'is_cloneable',
        # 'position',
        'success_page_title',
        'success_page_message',
        'action',
    )

    # In this way we keep possible trash out.
    for key in list(form_data.keys()):
        if key not in form_data_keys_whitelist:
            form_data.pop(key)
    # User information we always recreate!
    form_data['user'] = request.user

    try:
        form_data['event'] = Event.objects.get(id=form_data.get('event'))
    except Event.DoesNotExist:
        messages.warning(
            request,
            ('Event does not Exist!')
        )
        raise Http404('Event does not Exist!')

    form_entry = EventFormEntry(**form_data)

    form_entry.name += (" (imported on {0})").format(
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    form_entry.save()

    # One by one, importing form element plugins.
    for form_element_data in form_elements_data:
        if form_element_plugin_registry.registry.get(
                form_element_data.get('plugin_uid', None), None):
            form_element = FormElementEntry(**form_element_data)
            form_element.form_entry = form_entry
            form_element.save()
        else:
            if form_element_data.get('plugin_uid', None):
                messages.warning(
                    request,
                    'Plugin {0} is missing in the system.'
                )
            else:
                messages.warning(
                    request,
                    ugettext('Some essential plugin data missing in the JSON '
                             'import.')
                )

    # One by one, importing form handler plugins.
    for form_handler_data in form_handlers_data:
        if form_handler_plugin_registry.registry.get(
                form_handler_data.get('plugin_uid', None), None):
            form_handler = FormHandlerEntry(**form_handler_data)
            form_handler.form_entry = form_entry
            form_handler.save()
        else:
            if form_handler_data.get('plugin_uid', None):
                messages.warning(
                    request,
                    ugettext('Plugin {0} is missing in the system.').format(
                        form_handler_data.get('plugin_uid')
                    )
                )
            else:
                messages.warning(
                    request,
                    ugettext('Some essential data missing in the JSON '
                             'import.')
                )

    return form_entry
