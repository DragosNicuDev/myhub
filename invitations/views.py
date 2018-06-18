from email.mime.image import MIMEImage
import os

import simplejson as json

from django.core.mail import EmailMultiAlternatives, send_mail
from django.shortcuts import render
from django.views import generic
from django.template.loader import render_to_string
from django.urls import reverse

from anymail.message import AnymailMessage
from anymail.message import attach_inline_image_file, attach_inline_image

from .models import EventInvitation
from .forms import EventInvitationForm


def get_invitation_context():
    return {
        'title': "Lion's Head",
        'main_image': '2018-05-01.jpg',
        # 'logo': 'logo.gif',
        'main_color': '#fff3e8',
        'font_color': '#666666',
        'page_title': "Cory and Rowena - You're Invited!",
        'preheader_text': "You are invited!",
}


class EventInvitationCreate(generic.CreateView):
    model = EventInvitation
    form = EventInvitationForm
    fields = '__all__'
    template_name = 'control-panel/event-invitation/invitation_create.html'
    success_url = '/control-panel/invitations/'

    def form_valid(self, form):
        body = form.cleaned_data.get('body')
        event = form.cleaned_data.get('event')
        subject = form.cleaned_data.get('subject')
        emails = event.eventinvitee_set.values(
            'email',
            'first_name',
            'last_name',
            'token',
            )

        data = {}

        for invitee in emails:
            data.setdefault(invitee.get('email'), {})\
                .setdefault('first_name', invitee.get('first_name'))
            data.setdefault(invitee.get('email'), {})\
                .setdefault('last_name', invitee.get('last_name'))
            data.setdefault(invitee.get('email'), {})\
                .setdefault('token', 'http://localhost:8000/' + str(event.pk) + '/' + invitee.get('token'))

        recipients = []

        for email in emails:
            recipients.append(email.get('email'))

        message = AnymailMessage(
            subject=subject,
            body=body,
            to=recipients
        )

        message.merge_data = data
        message.merge_global_data = {
            'ship_date': "May 15",  # Anymail maps globals to all recipients
            'event': str(event),  # Anymail maps globals to all recipients
        }

        cid = attach_inline_image_file(
            message,
            os.path.join(os.path.dirname(__file__), 'static', 'photos', '2018-05-01.jpg')
        )

        # logo = attach_inline_image_file(
        #     message,
        #     os.path.join(os.path.dirname(__file__), 'static', 'photos', 'logo.gif'))
        context = get_invitation_context()
        context['main_image'] = cid
        # context['logo'] = logo
        context['body'] = body
        template_html = render_to_string('invitations/invitation.html', context=context)
        message.attach_alternative(template_html, "text/html")
        message.mixed_subtype = 'related'
        message.send()
        return super().form_valid(form)


class EventInvitationList(generic.ListView):
    model = EventInvitation
    template_name = 'control-panel/event-invitation/invitation_list.html'


class EventInvitationDetail(generic.DetailView):
    model = EventInvitation
    template_name = 'control-panel/event-invitation/invitation_detail.html'
