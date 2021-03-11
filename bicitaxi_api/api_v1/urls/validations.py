from django.urls import path
from django.conf.urls import url, include
from bicitaxi_api.api_v1.views import validations as validations_views

urlpatterns = [
    path('inside', validations_views.InsideValidationView.as_view()),
]
