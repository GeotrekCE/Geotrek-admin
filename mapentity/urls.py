from django.conf.urls import patterns, include, url

from screamshot.views import capture


urlpatterns = patterns('screamshot.views',
    url(r'^capture/$', capture, name='capture'),
)

