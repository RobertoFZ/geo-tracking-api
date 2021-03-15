from django.urls import path
from django.conf.urls import url, include
from bicitaxi_api.api_v1.views import report as report_views

urlpatterns = [
    path('', report_views.ReportView.as_view()),
]
