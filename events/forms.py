import socket

from six.moves.urllib.parse import urlparse

from django import forms
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext, ugettext_lazy as _

from .models import FobiTesting

from fobi.base import get_theme
from fobi.models import FormEntry, FormElementEntry
try:
    from ckeditor.widgets import CKEditorWidget
    CKEDITOR_INSTALLED = True
except ImportError:
    CKEDITOR_INSTALLED = False

# *****************************************************************************
# *****************************************************************************
# ******************************* Entry forms *********************************
# *****************************************************************************
# *****************************************************************************


class FormEntryForm(forms.ModelForm):
    """Form for ``fobi.models.FormEntry`` model."""

    class Meta(object):
        """Meta class."""

        model = FormEntry
        fields = (
            'name',
            'title',
            # 'event',
            'is_public',
            'active_date_from',
            'active_date_to',
            'inactive_page_title',
            'inactive_page_message',
            'success_page_title',
            'success_page_message',
            'action',
            # 'is_cloneable',
        )

    def __init__(self, *args, **kwargs):
        """Constructor."""
        self.request = kwargs.pop('request', None)
        if self.request is None:
            raise ImproperlyConfigured(
                ugettext(
                    "The {0} form requires a "
                    "request argument.".format(self.__class__.__name__)
                )
            )

        super(FormEntryForm, self).__init__(*args, **kwargs)
        theme = get_theme(request=None, as_instance=True)

        self.fields['name'].widget = forms.widgets.TextInput(
            attrs={'class': theme.form_element_html_class}
        )

        self.fields['title'].widget = forms.widgets.TextInput(
            attrs={'class': theme.form_element_html_class}
        )

        self.fields['success_page_title'].widget = forms.widgets.TextInput(
            attrs={'class': theme.form_element_html_class}
        )

        self.fields['inactive_page_title'].widget = forms.widgets.TextInput(
            attrs={'class': theme.form_element_html_class}
        )

        self.fields['active_date_from'].widget = forms.widgets.DateTimeInput(
            format='%Y-%m-%d %H:%M',
            attrs={'class': theme.form_element_html_class}
        )

        self.fields['active_date_to'].widget = forms.widgets.DateTimeInput(
            format='%Y-%m-%d %H:%M',
            attrs={'class': theme.form_element_html_class}
        )

        if CKEDITOR_INSTALLED:
            self.fields['success_page_message'].widget = CKEditorWidget(
                attrs={'class': theme.form_element_html_class}
            )
            self.fields['inactive_page_message'].widget = CKEditorWidget(
                attrs={'class': theme.form_element_html_class}
            )
        else:
            self.fields['success_page_message'].widget = forms.widgets.Textarea(
                attrs={'class': theme.form_element_html_class}
            )
            self.fields['inactive_page_message'].widget = forms.widgets.Textarea(
                attrs={'class': theme.form_element_html_class}
            )

        self.fields['action'].widget = forms.widgets.TextInput(
            attrs={'class': theme.form_element_html_class}
        )

        # At the moment this is done for Foundation 5 theme. Remove this once
        # it's possible for a theme to override this form. Alternatively, add
        # the attrs to the theme API.
        self.fields['is_public'].widget = forms.widgets.CheckboxInput(
            attrs={'data-customforms': 'disabled'}
        )
        # self.fields['is_cloneable'].widget = forms.widgets.CheckboxInput(
        #    attrs={'data-customforms': 'disabled'}
        # )

    def clean_action(self):
        """Validate the action (URL).

        Checks if URL exists.
        """
        url = self.cleaned_data['action']
        if url:
            full_url = url

            if not (url.startswith('http://') or url.startswith('https://')):
                full_url = self.request.build_absolute_uri(url)

            parsed_url = urlparse(full_url)

            local = False

            try:
                localhost = socket.gethostbyname('localhost')
            except Exception as err:
                localhost = '127.0.0.1'

            try:
                host = socket.gethostbyname(parsed_url.hostname)

                local = (localhost == host)
            except socket.gaierror as err:
                pass

            if local:
                full_url = parsed_url.path

            if not url_exists(full_url, local=local):
                raise forms.ValidationError(
                    ugettext("Invalid action URL {0}.").format(full_url)
                )

        return url


class _FormElementEntryForm(forms.ModelForm):
    """FormElementEntry form.

    To be used with `FormElementEntryFormSet` only.
    """

    class Meta(object):
        """Meta class."""

        model = FormElementEntry
        fields = ('position',)


FormElementEntryFormSet = modelformset_factory(
    FormElementEntry,
    fields=('position',),
    extra=0,
    form=_FormElementEntryForm
)
