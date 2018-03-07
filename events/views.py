from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext, ugettext_lazy as _


from fobi.dynamic import assemble_form_class
from fobi.settings import GET_PARAM_INITIAL_DATA, DEBUG
from fobi.base import get_theme, fire_form_callbacks, submit_plugin_form_data, run_form_handlers
from fobi.constants import (
    CALLBACK_BEFORE_FORM_VALIDATION,
    CALLBACK_FORM_VALID_BEFORE_SUBMIT_PLUGIN_FORM_DATA,
    CALLBACK_FORM_VALID,
    CALLBACK_FORM_VALID_AFTER_FORM_HANDLERS,
    CALLBACK_FORM_INVALID
)

from fobi.models import FormEntry
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
    # model = Event
    template_name = 'home.html'


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'

    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['date_time'] = EventDateAndTime.objects.first()
       context['description'] = EventDescription.objects.get(
           event__pk = self.object.pk
       )
       context['gmap_key'] = settings.EASY_MAPS_GOOGLE_MAPS_API_KEY
       context['location'] = EventLocation.objects.filter(
           event__id = self.object.pk
       )
       form_entry = FobiTesting.objects.select_related('user') \
                             .get(event__pk = self.object.pk)

       form_element_entries = form_entry.formelemententry_set.all()[:]
       form_cls = assemble_form_class(
           form_entry,
           form_element_entries=form_element_entries,
       )
       kwargs = {}
       if GET_PARAM_INITIAL_DATA in self.request.GET:
           kwargs = {'initial': self.request.GET}
       context['form'] = form_cls(**kwargs)
       return context


class FobiFormPOST(SingleObjectMixin, FormView):
    template_name = 'books/author_detail.html'

    def post(self, request, *args, **kwargs):

        form_entry = FobiTesting._default_manager.select_related('user') \
                          .get(event__pk = kwargs.get('pk'))
        form_element_entries = form_entry.formelemententry_set.all()[:]
        # This is where the most of the magic happens. Our form is being built
        # dynamically.
        form_cls = assemble_form_class(
            form_entry,
            form_element_entries=form_element_entries,
            request=request
        )

        # if not request.user.is_authenticated:
        #     return HttpResponseForbidden()
        # self.object = self.get_object()
        form = form_cls(request.POST, request.FILES)

        # Fire pre form validation callbacks
        fire_form_callbacks(form_entry=form_entry, request=request, form=form,
                            stage=CALLBACK_BEFORE_FORM_VALIDATION)

        if form.is_valid():
            # Fire form valid callbacks, before handling submitted plugin
            # form data.
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
                stage=CALLBACK_FORM_VALID_AFTER_FORM_HANDLERS
            )

            messages.info(
                request,
                ugettext("Form {0} was submitted successfully.").format(
                    form_entry.name
                )
            )
            return redirect(
                reverse('fobi.form_entry_submitted', args=[form_entry.slug])
            )
        return super().post(request, *args, **kwargs)


class EventDetail(View):
    def get(self, request, *args, **kwargs):
        view = EventDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = FobiFormPOST.as_view()
        return view(request, *args, **kwargs)
