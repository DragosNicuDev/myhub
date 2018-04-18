from __future__ import absolute_import

from django.apps import apps

from django.forms.fields import ChoiceField
from django.forms.models import ModelChoiceField

from events.form_utils import DragosChoiceField, get_select_field_cond_data
from django.forms.widgets import RadioSelect
from django.utils.translation import ugettext_lazy as _

from fobi.base import FormFieldPlugin, get_theme
from fobi.constants import (
    SUBMIT_VALUE_AS_VAL,
    SUBMIT_VALUE_AS_REPR
)
from fobi.helpers import (
    safe_text,
    get_app_label_and_model_name,
    get_model_name_for_object,
    get_select_field_choices
)

from events.models import Event
from . import UID
from .forms import DragosRadioInputForm
from .settings import SUBMIT_VALUE_AS

__title__ = 'fobi.contrib.plugins.form_elements.fields.radio.base'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2014-2018 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('DragosRadioInputPlugin',)

theme = get_theme(request=None, as_instance=True)


class DragosRadioInputPlugin(FormFieldPlugin):
    """Radio field plugin."""

    uid = UID
    name = _("Dragos Radio")
    group = _("Fields")
    form = DragosRadioInputForm

    def get_form_field_instances(self, request=None, form_entry=None,
                                 form_element_entries=None, **kwargs):
        """Get form field instances."""
        choices = get_select_field_choices(self.data.choices)
        conditioned_data = get_select_field_cond_data(self.data.conditioned_data)
        widget_attrs = {'class': theme.form_radio_element_html_class}

        field_kwargs = {
            'label': self.data.label,
            'help_text': self.data.help_text,
            'initial': self.data.initial,
            'required': self.data.required,
            'conditional': self.data.conditional,
            'conditioned_data': conditioned_data,
            'is_conditioned': self.data.is_conditioned,
            'choices': choices,
            'widget': RadioSelect(attrs=widget_attrs),
        }

        return [(self.data.name, DragosChoiceField, field_kwargs)]

    def submit_plugin_form_data(self, form_entry, request, form,
                                form_element_entries=None, **kwargs):
        """Submit plugin form data/process.

        :param fobi.models.FormEntry form_entry: Instance of
            ``fobi.models.FormEntry``.
        :param django.http.HttpRequest request:
        :param django.forms.Form form:
        """
        # In case if we should submit value as is, we don't return anything.
        # In other cases, we proceed further.
        if SUBMIT_VALUE_AS != SUBMIT_VALUE_AS_VAL:
            # Get the object
            value = form.cleaned_data.get(self.data.name, None)

            # Get choices
            choices = dict(get_select_field_choices(self.data.choices))
            conditioned_data = dict(get_select_field_choices(self.data.conditioned_data))

            if value in choices:
                # Handle the submitted form value

                label = safe_text(choices.get(value))

                # Should be returned as repr
                if SUBMIT_VALUE_AS == SUBMIT_VALUE_AS_REPR:
                    value = label
                # Should be returned as mix
                else:
                    value = "{0} ({1})".format(label, value)

                # Overwrite ``cleaned_data`` of the ``form`` with object
                # qualifier.
                form.cleaned_data[self.data.name] = value

                # It's critically important to return the ``form`` with updated
                # ``cleaned_data``
                return form
