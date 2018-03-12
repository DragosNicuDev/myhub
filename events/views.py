import simplejson as json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden, Http404
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext, ugettext_lazy as _


from fobi.base import get_theme, fire_form_callbacks, submit_plugin_form_data, run_form_handlers
from fobi.settings import GET_PARAM_INITIAL_DATA, DEBUG
from fobi.constants import (
    CALLBACK_BEFORE_FORM_VALIDATION,
    CALLBACK_FORM_VALID_BEFORE_SUBMIT_PLUGIN_FORM_DATA,
    CALLBACK_FORM_VALID,
    CALLBACK_FORM_VALID_AFTER_FORM_HANDLERS,
    CALLBACK_FORM_INVALID
)

from fobi.dynamic import assemble_form_class
from fobi.form_importers import (
    ensure_autodiscover as ensure_importers_autodiscover,
    form_importer_plugin_registry, get_form_importer_plugin_urls
)
from fobi.forms import ImportFormEntryForm
from fobi.helpers import JSONDataExporter
from fobi.decorators import permissions_required, SATISFY_ALL, SATISFY_ANY
from fobi.models import FormEntry
from .form_utils import prepare_form_entry_export_data, perform_form_entry_import

# Create your views here.
from .models import (
    Event,
    EventDateAndTime,
    EventDescription,
    EventLocation,
    EventInvitee,
    EventFobiForms,
    FobiTesting)


class EventTemplateView(TemplateView):
    template_name = 'home.html'


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'

    def get_object(self, queryset=None):
       return get_object_or_404(
            EventInvitee,
            event__pk = self.kwargs.get('pk'),
            token = self.kwargs.get('token')
        )

    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['event'] = Event.objects.get(
           pk = self.kwargs.get('pk')
       )
       context['date_time'] = EventDateAndTime.objects.get(
           event__pk = self.kwargs.get('pk')
       )
       context['description'] = EventDescription.objects.get(
           event__pk = self.kwargs.get('pk')
       )
       context['gmap_key'] = settings.EASY_MAPS_GOOGLE_MAPS_API_KEY
       context['location'] = EventLocation.objects.filter(
           event__pk = self.kwargs.get('pk')
       )
       context['invitee'] = EventInvitee.objects.filter(
           event__pk = self.kwargs.get('pk')
       )
       form_entry = FobiTesting.objects.select_related('user') \
                             .get(event__pk = self.kwargs.get('pk'))
       form_element_entries = form_entry.formelemententry_set.all()[:]
       form_cls = assemble_form_class(
           form_entry,
           form_element_entries=form_element_entries,
       )
       kwargs = {}
       context['form'] = form_cls(**kwargs)
       return context


class FobiFormPOST(SingleObjectMixin, FormView):
    template_name = 'events/event_detail.html'

    def get_success_url(self):
        return reverse('thank_you')

    def get_object(self, queryset=None):
       return get_object_or_404(
            EventInvitee,
            event__pk = self.kwargs.get('pk'),
            token = self.kwargs.get('token')
        )

    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['event'] = Event.objects.get(
           pk = self.kwargs.get('pk')
       )
       context['date_time'] = EventDateAndTime.objects.get(
           event__pk = self.kwargs.get('pk')
       )
       context['description'] = EventDescription.objects.get(
           event__pk = self.kwargs.get('pk')
       )
       context['gmap_key'] = settings.EASY_MAPS_GOOGLE_MAPS_API_KEY
       context['location'] = EventLocation.objects.filter(
           event__pk = self.kwargs.get('pk')
       )
       context['invitee'] = EventInvitee.objects.filter(
           event__pk = self.kwargs.get('pk')
       )
       return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_entry = FobiTesting._default_manager.select_related('user') \
                          .get(event__pk = self.kwargs.get('pk'))
        form_element_entries = form_entry.formelemententry_set.all()[:]
        # This is where the most of the magic happens. Our form is being built
        # dynamically.
        form_cls = assemble_form_class(
            form_entry,
            form_element_entries=form_element_entries,
            request=request
        )
        form = form_cls(request.POST, request.FILES)

        if form.is_valid():
            return self.form_valid(form, form_entry, request, form_element_entries)
        else:
            return self.form_invalid(form)


    def form_valid(self, form, form_entry, request, form_element_entries):
        # Fire pre form validation callbacks
        fire_form_callbacks(form_entry=form_entry, request=request, form=form,
            stage=CALLBACK_BEFORE_FORM_VALIDATION)

        form = fire_form_callbacks(
            form_entry=form_entry,
            request=request,
            form=form,
            stage=CALLBACK_FORM_VALID_BEFORE_SUBMIT_PLUGIN_FORM_DATA
        )

        # Fire plugin processors
        form = submit_plugin_form_data(
            form_entry=form_entry,
            request=request,
            form=form
        )

        # Fire form valid callbacks
        form = fire_form_callbacks(form_entry=form_entry,
            request=request, form=form,
            stage=CALLBACK_FORM_VALID)

        # Run all handlers
        handler_responses, handler_errors = run_form_handlers(
            form_entry=form_entry,
            request=request,
            form=form,
            form_element_entries=form_element_entries
        )

        # Warning that not everything went ok.
        if handler_errors:
            for handler_error in handler_errors:
                    messages.warning(
                    request,
                    ugettext("Error occurred: {0}.").format(handler_error)
                )

        # Fire post handler callbacks
        fire_form_callbacks(
            form_entry=form_entry,
            request=request,
            form=form,
            stage=CALLBACK_FORM_VALID_AFTER_FORM_HANDLERS)
        # Fire form valid callbacks, before handling submitted plugin
        # form data.

        messages.info(
            self.request,
            ugettext("Form was submitted successfully.")
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        form_entry = FobiTesting._default_manager.select_related('user') \
                          .get(event__pk = self.kwargs.get('pk'))
        form_element_entries = form_entry.formelemententry_set.all()[:]
        # This is where the most of the magic happens. Our form is being built
        # dynamically.
        form_cls = assemble_form_class(
            form_entry,
            form_element_entries=form_element_entries,
            request=self.request
        )
        form = form_cls(self.request.POST, self.request.FILES)
        # Fire post form validation callbacks
        fire_form_callbacks(form_entry=form_entry, request=self.request,
                            form=form, stage=CALLBACK_FORM_INVALID)
        messages.info(
            self.request,
            ugettext("There was an error. Please check the form.")
        )
        return super().form_invalid(form)


class EventDetail(View):
    def get(self, request, *args, **kwargs):
        view = EventDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = FobiFormPOST.as_view()
        return view(request, *args, **kwargs)


dashboard_permissions = [
    # Form
    'fobi.add_formentry',
    'fobi.change_formentry',
    'fobi.delete_formentry',
]


@login_required
@permissions_required(satisfy=SATISFY_ANY, perms=dashboard_permissions)
def dashboard(request, theme=None, template_name=None):
    """Dashboard.

    :param django.http.HttpRequest request:
    :param fobi.base.BaseTheme theme: Theme instance.
    :param string template_name:
    :return django.http.HttpResponse:
    """
    form_entries = FobiTesting._default_manager \
                            .filter(user__pk=request.user.pk) \
                            .select_related('user')

    context = {
        'form_entries': form_entries,
        'form_importers': get_form_importer_plugin_urls(),
    }

    # If given, pass to the template (and override the value set by
    # the context processor.
    if theme:
        context.update({'fobi_theme': theme})

    if not template_name:
        theme = get_theme(request=request, as_instance=True)
        template_name = theme.dashboard_template

    return render(request, template_name, context)

create_form_entry_permissions = [
    'fobi.add_formentry',
    'fobi.add_formelemententry',
    'fobi.add_formhandlerentry',
]
@login_required
@permissions_required(satisfy=SATISFY_ALL, perms=create_form_entry_permissions)
def event_export_form_entry(request, form_entry_id, template_name=None):
    """Export form entry to JSON.

    :param django.http.HttpRequest request:
    :param int form_entry_id:
    :param string template_name:
    :return django.http.HttpResponse:
    """
    try:
        form_entry = FobiTesting._default_manager \
                              .get(pk=form_entry_id, user__pk=request.user.pk)

    except ObjectDoesNotExist as err:
        raise Http404(ugettext("Form entry not found."))

    data = prepare_form_entry_export_data(form_entry)

    # data = {
    #     'name': form_entry.name,
    #     'slug': form_entry.slug,
    #     'is_public': False,
    #     'is_cloneable': False,
    #     # 'position': form_entry.position,
    #     'success_page_title': form_entry.success_page_title,
    #     'success_page_message': form_entry.success_page_message,
    #     'action': form_entry.action,
    #     'form_elements': [],
    #     'form_handlers': [],
    # }
    #
    # form_element_entries = form_entry.formelemententry_set.all()[:]
    # form_handler_entries = form_entry.formhandlerentry_set.all()[:]
    #
    # for form_element_entry in form_element_entries:
    #     data['form_elements'].append(
    #         {
    #             'plugin_uid': form_element_entry.plugin_uid,
    #             'position': form_element_entry.position,
    #             'plugin_data': form_element_entry.plugin_data,
    #         }
    #     )
    #
    # for form_handler_entry in form_handler_entries:
    #     data['form_handlers'].append(
    #         {
    #             'plugin_uid': form_handler_entry.plugin_uid,
    #             'plugin_data': form_handler_entry.plugin_data,
    #         }
    #     )

    data_exporter = JSONDataExporter(json.dumps(data), form_entry.slug)

    return data_exporter.export()


@login_required
@permissions_required(satisfy=SATISFY_ALL, perms=create_form_entry_permissions)
def event_import_form_entry(request, template_name=None):
    """Import form entry.

    :param django.http.HttpRequest request:
    :param string template_name:
    :return django.http.HttpResponse:
    """
    if request.method == 'POST':
        form = ImportFormEntryForm(request.POST, request.FILES)

        if form.is_valid():
            # Reading the contents of the file into JSON
            json_file = form.cleaned_data['file']
            file_contents = json_file.read()

            # This is the form data which we are going to use when recreating
            # the form.
            form_data = json.loads(file_contents)

            # Since we just feed all the data to the `FormEntry` class,
            # we need to make sure it doesn't have strange fields in.
            # Furthermore, we will use the `form_element_data` and
            # `form_handler_data` for filling the missing plugin data.
            form_entry = perform_form_entry_import(request, form_data)
            # form_elements_data = form_data.pop('form_elements', [])
            # form_handlers_data = form_data.pop('form_handlers', [])
            #
            # form_data_keys_whitelist = (
            #     'name',
            #     'slug',
            #     'is_public',
            #     'is_cloneable',
            #     # 'position',
            #     'success_page_title',
            #     'success_page_message',
            #     'action',
            # )
            #
            # # In this way we keep possible trash out.
            # for key in list(form_data.keys()):
            #     if key not in form_data_keys_whitelist:
            #         form_data.pop(key)
            #
            # # User information we always recreate!
            # form_data['user'] = request.user
            #
            # form_entry = FormEntry(**form_data)
            #
            # form_entry.name += ugettext(" (imported on {0})").format(
            #     datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # )
            # form_entry.save()
            #
            # # One by one, importing form element plugins.
            # for form_element_data in form_elements_data:
            #     if form_element_plugin_registry._registry.get(
            #             form_element_data.get('plugin_uid', None), None):
            #         form_element = FormElementEntry(**form_element_data)
            #         form_element.form_entry = form_entry
            #         form_element.save()
            #     else:
            #         if form_element_data.get('plugin_uid', None):
            #             messages.warning(
            #                 request,
            #                 _('Plugin {0} is missing in the system.'
            #                   '').format(form_element_data.get('plugin_uid'))
            #             )
            #         else:
            #             messages.warning(
            #                 request,
            #                 _('Some essential plugin data missing in the '
            #                   'JSON import.')
            #             )
            #
            # # One by one, importing form handler plugins.
            # for form_handler_data in form_handlers_data:
            #     if form_handler_plugin_registry._registry.get(
            #             form_handler_data.get('plugin_uid', None), None):
            #         form_handler = FormHandlerEntry(**form_handler_data)
            #         form_handler.form_entry = form_entry
            #         form_handler.save()
            #     else:
            #         if form_handler.get('plugin_uid', None):
            #             messages.warning(
            #                 request,
            #                 _('Plugin {0} is missing in the system.'
            #                   '').format(form_handler.get('plugin_uid'))
            #             )
            #         else:
            #             messages.warning(
            #                 request,
            #                 _('Some essential data missing in the JSON '
            #                   'import.')
            #             )

            messages.info(
                request,
                _('The form was imported successfully.')
            )
            return redirect(
                'fobi.edit_form_entry', form_entry_id=form_entry.pk
            )
    else:
        form = ImportFormEntryForm()

    # When importing entries from saved JSON we shouldn't just save
    # them into database and consider it done, since there might be cases
    # if a certain plugin doesn't exist in the system, which will lead
    # to broken form entries. Instead, we should check every single
    # form-element or form-handler plugin for existence. If not doesn't exist
    # in the system, we might: (1) roll entire transaction back or (2) ignore
    # broken entries. The `ImportFormEntryForm` form has two fields to
    # additional fields which serve the purpose:
    # `ignore_broken_form_element_entries` and
    # `ignore_broken_form_handler_entries`. When set to True, when a broken
    # form element/handler plugin has been discovered, the import would
    # continue, having the broken form element/handler entries not imported.

    context = {
        'form': form,
        # 'form_entry': form_entry
    }

    if not template_name:
        theme = get_theme(request=request, as_instance=True)
        template_name = theme.import_form_entry_template

    return render(request, template_name, context)
