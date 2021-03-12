from django.urls import path
from django.conf.urls import url, include
from bicitaxi_api.api_v1.views import locations as locations_views

urlpatterns = [
    path('', locations_views.LocationsView.as_view()),
    path('<int:location_pk>', locations_views.LocationView.as_view()),
    path('last', locations_views.LastLocationsView.as_view()),
]
