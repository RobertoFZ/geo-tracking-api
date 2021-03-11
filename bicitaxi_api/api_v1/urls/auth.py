from django.urls import path

from bicitaxi_api.api_v1.views import auth as auth_views

urlpatterns = [
    # Authentication
    path('login', auth_views.AuthView.as_view()),
    path('reset', auth_views.ResetPasswordView.as_view()),
]
