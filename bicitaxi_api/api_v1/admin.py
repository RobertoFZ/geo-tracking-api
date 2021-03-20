from django.contrib import admin
from bicitaxi_api.api_v1.models import (
    User,
    Profile,
    Location,
    LocationZone,
    LocationZonePoint,
    LocationAssignation
)

# Register your models here.
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Location)
admin.site.register(LocationZone)
admin.site.register(LocationZonePoint)
admin.site.register(LocationAssignation)
