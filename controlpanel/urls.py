from django.conf.urls import include, url

from events.views import ReportsTemplateView
from invitations import views


urlpatterns = [
    url(r'^invitations/$',
        views.EventInvitationList.as_view(),
        name='invitation_list'),

    url(r'^invitations/create/$',
        views.EventInvitationCreate.as_view(),
        name='invitation_create'),

    url(r'^invitations/(?P<pk>\d+)/$',
        views.EventInvitationDetail.as_view(),
        name='invitation_detail'),

    url(r'^(?P<pk>\d+)/reports/$',
        ReportsTemplateView.as_view(),
        name='reports'),
]
