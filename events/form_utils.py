import datetime

from django.contrib import messages
from django.http import Http404

from .models import Event, FobiTesting

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

    form_entry = FobiTesting(**form_data)

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
