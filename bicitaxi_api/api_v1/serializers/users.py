from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from bicitaxi_api.api_v1.models import LocationAssignation
from bicitaxi_api.api_v1.functions import distance_between_two_points
from bicitaxi_api.api_v1.serializers.location_assignations import LocationAssignationSerializer
import datetime

from bicitaxi_api.api_v1.models import (
    User,
    Profile,
    Location
)
from bicitaxi_api.settings import URL_SERVER


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["locale", "phone", "municipality"]


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, label="user id")
    email = serializers.CharField(required=True, label="email")
    token = serializers.SerializerMethodField()
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "on_route",
            "password",
            "is_active",
            "token",
            "profile",
            "role"
        ]
        read_only_fields = ["id", "token", "role"]

    def create(self, validated_data):
        profile_data = validated_data.pop("profile")
        user = User.objects.create(**validated_data)
        user.set_password(validated_data["password"])

        profile = Profile.objects.create(user=user, **profile_data)
        user.profile = profile

        user.save()
        return user

    def validate(self, data):
        keys = data.keys()
        try:
            user = User.objects.get(email=data["email"])
            if "id" in keys:
                if not user.id == data["id"]:
                    raise serializers.ValidationError(
                        _(
                            "El correo %(email)s ya se encuentra en uso"
                            % {"email": data["email"]}
                        )
                    )
                else:
                    return data
            else:
                raise serializers.ValidationError(
                    _(
                        "El correo %(email)s ya se encuentra en uso"
                        % {"email": data["email"]}
                    )
                )
        except User.DoesNotExist:
            return data
        return data

    def get_token(self, data):
        if data.id:
            token, created = Token.objects.get_or_create(user__id=data.id)
            return token.key
        else:
            return None


class UserSimpleSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, label="user id")
    profile = ProfileSerializer()
    assignation = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "on_route",
            "profile",
            "assignation"
        ]
        read_only_fields = ["id"]

    def get_assignation(self, data):
        try:
            assignation = LocationAssignation.objects.get(user=data)
            return {
                'user_id': assignation.user_id,
                'location_zone_id': assignation.location_zone_id,
                'location_zone': {
                    'id': assignation.location_zone.id,
                    'name': assignation.location_zone.name
                }
            }
        except LocationAssignation.DoesNotExist:
            return None


class UserActivitySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, label="user id")
    profile = serializers.SerializerMethodField()
    activity = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "on_route",
            "profile",
            "activity",
        ]
        read_only_fields = ["id"]

    def get_profile(self, user):
        return ProfileSerializer(Profile.objects.get(user=user)).data

    def get_activity(self, user):
        morning_start = datetime.datetime.now().replace(hour=8, minute=0, second=0)
        morning_end = datetime.datetime.now().replace(hour=14, minute=0, second=0)
        evening_start = datetime.datetime.now().replace(hour=15, minute=0, second=0)
        evening_end = datetime.datetime.now().replace(hour=23, minute=0, second=0)

        morning_registers = Location.objects.filter(
            user=user, date__range=(morning_start, morning_end))
        
        evening_registers = Location.objects.filter(
            user=user, date__range=(evening_start, evening_end))

        distance = 0.0
        time = 0.0

        last_register = None
        for register in morning_registers:
            if last_register:
                distance += distance_between_two_points(
                    last_register, register)
            last_register = register
        
        if len(morning_registers) > 1:
            diff = morning_registers[0].date - morning_registers[len(morning_registers) - 1].date

            days, seconds = diff.days, diff.seconds
            hours = days * 24 + seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            time += minutes
        
        last_register = None
        for register in evening_registers:
            if last_register:
                distance += distance_between_two_points(
                    last_register, register)
            last_register = register
        
        if len(evening_registers) > 1:
            diff = evening_registers[0].date - evening_registers[len(evening_registers) - 1].date

            days, seconds = diff.days, diff.seconds
            hours = days * 24 + seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            time += minutes

        return {
            'time': time,
            'distance': distance
        }
