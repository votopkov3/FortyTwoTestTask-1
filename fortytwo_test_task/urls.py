from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static

admin.autodiscover()

urlpatterns = patterns(
    '',
    # Examples:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('apps.hello.urls', namespace="hello")),
    ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)