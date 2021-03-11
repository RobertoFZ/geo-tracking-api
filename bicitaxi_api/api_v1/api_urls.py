from django.urls import path
from django.conf.urls import url, include
from bicitaxi_api.api_v1.urls import users
from bicitaxi_api.api_v1.urls import locations
from bicitaxi_api.api_v1.urls import location_zones
from bicitaxi_api.api_v1.urls import validations
from bicitaxi_api.api_v1.urls import auth


urlpatterns = [
    # Base URL's
    path("users/", include((users, "users"))),
    path("locations/", include((locations, "locations"))),
    path("location_zones/", include((location_zones, "location zones"))),
    path("validations/", include((validations, "validations"))),
    path("auth/", include((auth, "auth"))),
]
