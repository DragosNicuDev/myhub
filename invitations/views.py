# -*- coding: utf-8 -*-

from email.mime.image import MIMEImage
import os

import simplejson as json

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.shortcuts import render
from django.views import generic
from django.template.loader import render_to_string
from django.urls import reverse

from anymail.message import AnymailMessage
from anymail.message import attach_inline_image_file

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
        subject_ro = form.cleaned_data.get('subject_ro')
        subject_en = form.cleaned_data.get('subject_en')
        emails = event.eventinvitee_set.values(
            'email',
            'first_name',
            'last_name',
            'language',
            'token',
            )

        data = {}

        for invitee in emails:
            data.setdefault(invitee.get('email'), {})\
                .setdefault('first_name', invitee.get('first_name'))
            data.setdefault(invitee.get('email'), {})\
                .setdefault('last_name', invitee.get('last_name'))
            data.setdefault(invitee.get('email'), {})\
                .setdefault('token', 'https://myhub.events/' + invitee.get('language') + '/' + str(event.pk) + '/' + invitee.get('token'))


        # print(data)

        recipients_en = []
        recipients_ro = []

        for email in emails:
            if email.get('language') == 'ro':
                recipients_ro.append(email.get('email'))
            if email.get('language') == 'en':
                recipients_en.append(email.get('email'))

        message_ro = AnymailMessage(
            subject=subject_ro,
            body=body,
            to=recipients_ro
        )

        message_ro.merge_data = data
        message_ro.merge_global_data = {
            'event': str(event),  # Anymail maps globals to all recipients
        }

        context = get_invitation_context()

        context['body'] = body
        template_html = render_to_string('invitations/invitation_ro.html', context=context)
        message_ro.attach_alternative(template_html, "text/html")
        message_ro.mixed_subtype = 'related'
        message_ro.esp_extra = {
            'o:tag': ["Invitatii nunta",]  # use Mailgun's test mode
        }
        message_ro.send()

        message_en = AnymailMessage(
            subject=subject_en,
            body=body,
            to=recipients_en
        )

        message_en.merge_data = data
        message_en.merge_global_data = {
            'event': str(event),  # Anymail maps globals to all recipients
        }

        context = get_invitation_context()

        context['body'] = body
        template_html = render_to_string('invitations/invitation_en.html', context=context)
        message_en.attach_alternative(template_html, "text/html")
        message_en.mixed_subtype = 'related'
        message_en.esp_extra = {
            'o:tag': ["Wedding Invitations",]  # use Mailgun's test mode
        }
        message_en.send()
        return super().form_valid(form)


class EventInvitationList(generic.ListView):
    model = EventInvitation
    template_name = 'control-panel/event-invitation/invitation_list.html'


class EventInvitationDetail(generic.DetailView):
    model = EventInvitation
    template_name = 'control-panel/event-invitation/invitation_detail.html'
