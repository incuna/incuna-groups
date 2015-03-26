from django.conf.urls import include, url
from django.contrib import admin
from incuna_test_utils.compat import DJANGO_LT_17


if DJANGO_LT_17:
    admin.autodiscover()


urlpatterns = [
    url(r'^groups/', include('groups.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
