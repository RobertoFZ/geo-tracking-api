from django.urls import path
from django.conf.urls import url, include
from bicitaxi_api.api_v1.views import users as users_views

urlpatterns = [
    path('', users_views.UsersView.as_view()),
    path('<int:user_pk>', users_views.UserView.as_view()),
    # path('<int:user_pk>/notebooks/', include((notebooks_urls, 'notebooks urls'))),
]
