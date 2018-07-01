from django import forms
from django.forms.widgets import Textarea
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _

from fobi.base import BasePluginForm, get_theme

from .settings import ALLOWED_TAGS, ALLOWED_ATTRIBUTES

try:
    import bleach
    BLEACH_INSTALLED = True
except ImportError as err:
    BLEACH_INSTALLED = False

__title__ = 'dragos_content_text.forms'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2014-2018 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('DragosContentTextForm',)


theme = get_theme(request=None, as_instance=True)


class DragosContentTextForm(forms.Form, BasePluginForm):
    """Form for ``ContentTextPlugin``."""

    plugin_data_fields = [
        ("text", ""),
        ("ro_text", ""),
        ("conditional", ""),
        ("conditioned_data", ""),
        ("is_conditioned", ""),
    ]

    text = forms.CharField(
        label=_("Text"),
        required=True,
        widget=Textarea(attrs={'class': theme.form_element_html_class})
    )
    ro_text = forms.CharField(
        label=_("Romanian Text"),
        required=True,
        widget=Textarea(attrs={'class': theme.form_element_html_class})
    )
    conditional = forms.CharField(
        label=_("Conditional"),
        # choices=[],
        required=False,
        widget=forms.widgets.TextInput(
            attrs={'class': theme.form_element_html_class}
        )
    )
    conditioned_data = forms.CharField(
        label=_("Conditioned Element"),
        required=False,
        widget=forms.widgets.Textarea(
            attrs={'class': theme.form_element_html_class}
        )
    )
    is_conditioned = forms.BooleanField(
        label=_("Is Conditioned"),
        # choices=[],
        required=False,
        widget=forms.widgets.CheckboxInput(
            attrs={'class': theme.form_element_checkbox_html_class}
        )
    )

    def clean_text(self):
        """Clean text value."""
        if BLEACH_INSTALLED:
            return bleach.clean(
                text=self.cleaned_data['text'],
                ro_text=self.cleaned_data['ro_text'],
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRIBUTES,
                strip=True,
                strip_comments=True
            )
        else:
            return strip_tags(
                self.cleaned_data['text'],
                self.cleaned_data['ro_text'],
            )
