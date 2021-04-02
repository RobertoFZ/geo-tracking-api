from django.utils.translation import activate, ugettext_lazy as _

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from datetime import datetime

from bicitaxi_api.api_v1.models import User, Profile
from bicitaxi_api.common.pagination import PaginationHandlerMixin
from bicitaxi_api.settings import URL_SERVER
from bicitaxi_api.api_v1.serializers.users import UserSerializer, UserSimpleSerializer


class UsersView(APIView, PaginationHandlerMixin):
    serializer_class = UserSerializer
    serializer_data_class = UserSimpleSerializer
    pagination_class = LimitOffsetPagination

    def get(self, request):
        if request.user.is_anonymous or request.user.role != 'admin':
            return
        params = request.query_params.keys()

        users = User.objects.all().order_by('first_name')
        for user in users:
            user.profile = Profile.objects.get(user=user)
        page = self.paginate_queryset(users)
        if page is not None and 'limit' in params:
            response = self.get_paginated_response(self.serializer_data_class(page, many=True).data)
        else:
            response = self.serializer_data_class(users, many=True)
        return Response(response.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = serializer.create(serializer.validated_data)

            token, created = Token.objects.get_or_create(user=user)

            response = self.serializer_class(user).data

            return Response(response, status=status.HTTP_201_CREATED)
        error_response = {
            "message": _("Error al crear al usuario"),
            "errors": serializer.errors,
        }
        return Response(error_response, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class UserView(APIView):

    serializer_class = UserSerializer

    def get(self, request, user_pk):
        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            return Response(
                {"message": _("Usuario no encontrado")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user == user:
            user.profile = Profile.objects.get(user=user)
            serializer = self.serializer_class_data(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": _("No tienes permisos para realizar está acción.")},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def put(self, request, user_pk):
        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            return Response(
                {"message": _("Usuario no encontrado")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user == user:
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid():
                user.profile = Profile.objects.get(user=user)
                user = serializer.update(user, serializer.validated_data)
                serializer = self.serializer_class(user)

                token, created = Token.objects.get_or_create(user=request.user)

                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        "message": _("Error al actualizar al usuario"),
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"message": _("No tienes permisos para realizar está acción.")},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def patch(self, request, user_pk):
        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            return Response(
                {"message": _("Usuario no encontrado")},
                status=status.HTTP_404_NOT_FOUND,
            )
        user.on_route = request.data['on_route']
        user.save()
        user.profile = Profile.objects.get(user=user)
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, user_pk):
        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            return Response(
                {"message": _("Usuario no encontrado")},
                status=status.HTTP_404_NOT_FOUND,
            )
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class UserChangePasswordView(APIView):
    serializer_class = AuthTokenSerializer

    def post(self, request, user_pk):
        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            return Response(
                {"message": _("Usuario no encontrado")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user == user:
            old_password = request.data["old_password"]
            password = request.data["password"]
            confirm = request.data["password_confirm"]

            serializer = self.serializer_class(
                data={"username": user.email, "password": old_password}
            )
            if serializer.is_valid():
                if password != confirm:
                    return Response(
                        {"message": "Las contraseñas no coinciden"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                user.set_password(password)
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                response = {
                    "message": _("La contraseña actual es inválida."),
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": _("No tienes permisos para realizar está acción.")},
                status=status.HTTP_401_UNAUTHORIZED,
            )
