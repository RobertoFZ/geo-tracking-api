from django.urls import path
from django.conf.urls import url, include
from bicitaxi_api.api_v1.views import location_zones as location_zones_views

urlpatterns = [
    path('', location_zones_views.LocationZonesView.as_view()),
    path('<int:location_zone_pk>', location_zones_views.LocationZoneView.as_view()),
    path('activity', location_zones_views.LocationZoneUsersView.as_view()),
]
