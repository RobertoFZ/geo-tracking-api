from django.utils.translation import ugettext as _

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from datetime import datetime, date

from bicitaxi_api.api_v1.models import LocationZone, LocationZonePoint, LocationAssignation
from bicitaxi_api.common.pagination import PaginationHandlerMixin
from bicitaxi_api.settings import URL_SERVER
from bicitaxi_api.api_v1.serializers.location_assignations import LocationAssignationSerializer


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class LocationAssignationsView(APIView, PaginationHandlerMixin):
    serializer_class = LocationAssignationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if request.user.role != 'admin':
            error_response = {
                "message": _("No tienes permisos para realizar esta acción"),
                "errors": [],
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            try:
                existing_record = LocationAssignation.objects.filter(user_id=request.data['user_id'])
                existing_record.delete()
            except:
                pass
            location_assignation = serializer.create(serializer.validated_data)
            response = self.serializer_class(location_assignation).data
            return Response(response, status=status.HTTP_201_CREATED)
        error_response = {
            "message": _("Error al crear la zona"),
            "errors": serializer.errors,
        }
        return Response(error_response, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class LocationAssignationView(APIView):
    serializer_class = LocationAssignationSerializer

    def get(self, request, location_assignation_pk):
        try:
            location_zone = LocationAssignation.objects.get(
                pk=location_assignation_pk)
        except LocationAssignation.DoesNotExist:
            return Response(
                {"message": _("Asignación no encontrada")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.role == 'admin':
            serializer = self.serializer_class(data=location_zone)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": _("No tienes permisos para realizar está acción.")},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def delete(self, request, location_assignation_pk):
        try:
            location_zone = LocationAssignation.objects.get(
                pk=location_assignation_pk)
        except LocationAssignation.DoesNotExist:
            return Response(
                {"message": _("Zona no encontrada")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.role == 'admin':
            location_zone.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"message": _("No tienes permisos para realizar está acción.")},
                status=status.HTTP_401_UNAUTHORIZED,
            )
