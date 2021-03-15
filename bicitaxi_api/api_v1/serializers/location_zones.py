from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from bicitaxi_api.api_v1.models import (
    LocationZone,
    LocationZonePoint
)
from bicitaxi_api.settings import URL_SERVER
from bicitaxi_api.api_v1.serializers.location_zone_points import LocationZonePointSerializer


class LocationZoneSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, label="location id")
    name = serializers.CharField(required=True, label="location zone name")
    color = serializers.CharField(required=False, label="location zone color")
    points = serializers.SerializerMethodField()

    class Meta:
        model = LocationZone
        fields = [
            "id",
            "color",
            "name",
            "points"
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        location_zone = LocationZone.objects.create(**validated_data)
        location_zone.save()
        return location_zone

    def get_points(self, location_zone):
        points = LocationZonePoint.objects.filter(location_zone=location_zone)
        return LocationZonePointSerializer(points, many=True).data
