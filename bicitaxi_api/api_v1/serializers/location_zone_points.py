from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from bicitaxi_api.api_v1.models import (
    LocationZonePoint
)
from bicitaxi_api.settings import URL_SERVER


class LocationZonePointSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, label="location id")
    latitude = serializers.CharField(required=True, label="location zone latitude")
    longitude = serializers.CharField(required=True, label="location zone longitude")
    order = serializers.IntegerField(required=True, label="location zone order")

    class Meta:
        model = LocationZonePoint
        fields = [
            "id",
            "latitude",
            "longitude",
            "order"
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        location_zone = LocationZonePoint.objects.create(**validated_data)
        location_zone.save()
        return location_zone
