from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('dashboard.urls', namespace='dashboard'))
]

if 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
