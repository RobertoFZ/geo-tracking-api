from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from bicitaxi_api.api_v1.models import (
    User,
    Location,
)
from bicitaxi_api.settings import URL_SERVER


class LocationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, label="location id")
    user_id = serializers.IntegerField(required=True, label="user id")
    latitude = serializers.CharField(required=True, label="latitude")
    longitude = serializers.CharField(required=True, label="longitude")

    class Meta:
        model = Location
        fields = [
            "id",
            "user_id",
            "date",
            "latitude",
            "longitude",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        location = Location.objects.create(**validated_data)
        location.save()
        return location
