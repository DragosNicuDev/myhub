import datetime

import simplejson as json

from fobi.base import (
    FormCallback,
    get_processed_form_data,
)
from fobi.constants import CALLBACK_FORM_VALID
from eventsformdatabase.models import SavedEventFormDataEntry
from events.models import EventInvitee

__title__ = 'fobi.contrib.plugins.form_handlers.db_store.callbacks'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2014-2018 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = (
    'AutoFormDbStore',
)


class AutoFormDbStore(FormCallback):
    """Auto save form entries.

    Note, that this callback is not active. In order to activate it, you
    should import the ``AutoFormDbStore`` and register it using the
    callback register as follows.

    >>> from fobi.base import form_callback_registry
    >>> from fobi.contrib.plugins.form_handlers.db_store.callbacks import (
    >>>     AutoFormDbStore
    >>> )
    >>> form_callback_registry.register(AutoFormDbStore)
    """

    stage = CALLBACK_FORM_VALID

    def callback(self, form_entry, request, form):
        """Callback.

        :param form_entry:
        :param request:
        :param form:
        :return:
        """
        form_element_entries = form_entry.formelemententry_set.all()

        # Clean up the values, leave our content fields and empty values.
        field_name_to_label_map, cleaned_data = get_processed_form_data(
            form,
            form_element_entries
        )

        for key, value in cleaned_data.items():
            if isinstance(value, (datetime.datetime, datetime.date)):
                cleaned_data[key] = value.isoformat() \
                    if hasattr(value, 'isoformat') \
                    else value

        gigi = EventInvitee.objects\
                .values_list('first_name', 'last_name', 'email')\
                .get(token = request.path.split('/')[-2])

        formatted_data = [
                {
                'label': value,
                'html_name': key,
                'answer': cleaned_data.get(key, ''),
                'first_name': gigi[0],
                'last_name': gigi[1],
                'email': gigi[2]}
                 for key, value in field_name_to_label_map.items()]

        answer = {}
        for y in formatted_data:
            if type(y['answer']) is list:
                for an in y['answer']:
                    answer.setdefault(y['label'], {})\
                        .setdefault('answer', []).append(an)
                    answer.setdefault(y['label'], {}).setdefault('full_name', []).append(y['first_name'] + ' ' + y['last_name'])
                    answer.setdefault(y['label'], {}).setdefault('email', []).append(y['email'])
            elif type(y['answer']) is str:
                answer.setdefault(y['label'], {})\
                    .setdefault('answer', []).append(y['answer'])
                answer.setdefault(y['label'], {}).setdefault('full_name', []).append(y['first_name'] + ' ' + y['last_name'])
                answer.setdefault(y['label'], {}).setdefault('email', []).append(y['email'])

        saved_form_data_entry = SavedEventFormDataEntry(
            form_entry=form_entry,
            user=request.user if request.user and request.user.pk else None,
            form_data_headers=json.dumps(field_name_to_label_map),
            saved_data=json.dumps(cleaned_data),
            dragos_saved_data=json.dumps(answer),
            invitee=EventInvitee.objects.get(token = request.path.split('/')[-2])
        )
        saved_form_data_entry.save()
