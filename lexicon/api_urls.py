from rest_framework import routers

from django.conf.urls import url, include

from . import api_views


router = routers.DefaultRouter()
router.register(r'lexicalentries', api_views.LexicalEntryViewSet)
router.register(r'lexicalentries_tei', api_views.LexicalEntryTEIViewSet)


urlpatterns = [
    url(r'', include(router.urls)),
    url(
        r'api-auth/',
        include('rest_framework.urls', namespace='rest_framework')
    ),
]
