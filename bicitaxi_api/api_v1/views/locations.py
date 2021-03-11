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

from bicitaxi_api.api_v1.models import User, Location
from bicitaxi_api.common.pagination import PaginationHandlerMixin
from bicitaxi_api.settings import URL_SERVER
from bicitaxi_api.api_v1.serializers.locations import LocationSerializer


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class LocationsView(APIView, PaginationHandlerMixin):
    serializer_class = LocationSerializer

    def get(self, request):
        locations = []
        keys = request.query_params.keys()

        if 'from' in keys and not 'to' in keys:
            error_response = {
                "message": _("Se debe indicar los valores 'from' y 'to' para hacer el filtrado por fecha"),
                "errors": [],
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        if 'from' in keys and 'to' in keys:
            start_date_string = request.query_params['from']
            end_date_string = request.query_params['to']

            start_date = datetime.strptime(
                start_date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
            end_date = datetime.strptime(
                end_date_string, '%Y-%m-%dT%H:%M:%S.%fZ')

            if end_date < start_date:
                error_response = {
                    "message": _("La fecha de fin no puede ser menor a la fecha de inicio"),
                    "errors": [],
                }
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

            locations = Location.objects.filter(
                date__range=[start_date, end_date])
        else:
            locations = Location.objects.all()
        response = self.serializer_class(locations, many=True).data
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            location = serializer.create(serializer.validated_data)
            response = self.serializer_class(location).data
            return Response(response, status=status.HTTP_201_CREATED)
        error_response = {
            "message": _("Error al crear la ubicación"),
            "errors": serializer.errors,
        }
        return Response(error_response, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class LocationView(APIView):
    serializer_class = LocationSerializer

    def get(self, request, location_pk):
        try:
            location = Location.objects.get(pk=location_pk)
        except Location.DoesNotExist:
            return Response(
                {"message": _("Ubicación no encontrada")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.role == 'admin':
            serializer = self.serializer_class(data=location)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": _("No tienes permisos para realizar está acción.")},
                status=status.HTTP_401_UNAUTHORIZED,
            )