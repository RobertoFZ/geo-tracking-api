from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from bicitaxi_api.api_v1.models import (
    LocationAssignation,
)
from bicitaxi_api.api_v1.serializers.location_zones import LocationZoneSerializer
from bicitaxi_api.settings import URL_SERVER


class LocationAssignationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, label="location id")
    user_id = serializers.IntegerField(required=True, label="user id")
    location_zone_id = serializers.IntegerField(
        required=True, label="location zone id")
    location_zone = LocationZoneSerializer(read_only=True)

    class Meta:
        model = LocationAssignation
        fields = [
            "id",
            "user_id",
            "location_zone_id",
            "location_zone"
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        location = LocationAssignation.objects.create(**validated_data)
        location.save()
        return location
