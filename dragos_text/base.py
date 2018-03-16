from __future__ import absolute_import

from django.forms.fields import CharField
from django.forms.widgets import TextInput
from django.utils.translation import ugettext_lazy as _

from fobi.base import FormFieldPlugin, get_theme

from . import UID
from .forms import DragosTextInputForm

from events.form_utils import DragosCharField, get_select_field_cond_data

__title__ = 'dragos_text.base'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2014-2018 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('DragosTextInputPlugin',)

theme = get_theme(request=None, as_instance=True)


class DragosTextInputPlugin(FormFieldPlugin):
    """Text field plugin."""

    uid = UID
    name = _("Dragos Text")
    group = _("Fields")
    form = DragosTextInputForm

    def get_form_field_instances(self, request=None, form_entry=None,
                                 form_element_entries=None, **kwargs):
        """Get form field instances."""
        widget_attrs = {
            'class': theme.form_element_html_class,
            'placeholder': self.data.placeholder,
        }
        conditioned_data = get_select_field_cond_data(self.data.conditioned_data)

        field_kwargs = {
            'label': self.data.label,
            'help_text': self.data.help_text,
            'initial': self.data.initial,
            'conditional': self.data.conditional,
            'conditioned_data': conditioned_data,
            'is_conditioned': self.data.is_conditioned,
            'required': self.data.required,
            'widget': TextInput(attrs=widget_attrs),
        }
        if self.data.max_length is not None:
            field_kwargs['max_length'] = int(self.data.max_length)

        return [(self.data.name, DragosCharField, field_kwargs)]
