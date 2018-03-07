from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views

from events.views import EventTemplateView, EventDetail

urlpatterns = [
    url(r'^$', EventTemplateView.as_view(), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),

    # Fobi View URLs
    url(r'^fobi/', include('fobi.urls.view')),

    # Fobi Edit URLs
    url(r'^fobi/', include('fobi.urls.edit')),

    url(r'^summernote/', include('django_summernote.urls')),

    # Fobi DB Store plugin URLs
    url(r'^fobi/plugins/form-handlers/db-store/',
        include('fobi.contrib.plugins.form_handlers.db_store.urls')),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),

    # User management
    url(r'^users/', include('myhub_events.users.urls', namespace='users')),
    url(r'^accounts/', include('allauth.urls')),

    # Your stuff: custom urls includes go here
    url(r'^i18n/', include('django.conf.urls.i18n')),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    # url(r'^$', EventTemplateView.as_view(), name='home'),
    url(r'^(?P<pk>\d+)/$', EventDetail.as_view(), name='event-detail'),
    # url(r'^accounts/', include('allauth.urls')),
    # url(r'^users/', include('myhub_events.users.urls', namespace='users')),

    prefix_default_language=False
)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

admin.site.site_header = "MyHub Events Admin"
admin.site.site_title = "MyHub Events Admin Portal"
admin.site.index_title = "Welcome to MyHub Events"
