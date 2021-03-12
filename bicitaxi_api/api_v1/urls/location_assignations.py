from django.urls import path
from django.conf.urls import url, include
from bicitaxi_api.api_v1.views import location_assignations as location_assignations_views

urlpatterns = [
    path('', location_assignations_views.LocationAssignationsView.as_view()),
    path('<int:location_assignation_pk>',
         location_assignations_views.LocationAssignationView.as_view()),
]
