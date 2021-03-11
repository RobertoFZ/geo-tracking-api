from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from bicitaxi_api.api_v1.models import (
    User,
    Profile,
)
from bicitaxi_api.settings import URL_SERVER


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["locale"]


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
