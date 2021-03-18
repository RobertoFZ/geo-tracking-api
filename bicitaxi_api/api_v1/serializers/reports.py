from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from bicitaxi_api.api_v1.serializers.locations import LocationSerializer
from bicitaxi_api.api_v1.serializers.location_zones import LocationZoneSerializer
from bicitaxi_api.api_v1.serializers.users import UserSimpleSerializer

from bicitaxi_api.api_v1.models import (
    User,
    Location,
)
from bicitaxi_api.settings import URL_SERVER


class ReportSerializer(serializers.Serializer):
    locations = LocationSerializer(read_only=True, many=True)
    location_zone = LocationZoneSerializer(read_only=True)
    user = UserSimpleSerializer(read_only=True)
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    time = serializers.IntegerField()
