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
from bicitaxi_api.api_v1.serializers.location_zones import LocationZoneSerializer
from bicitaxi_api.api_v1.serializers.users import UserActivitySerializer


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class LocationZonesView(APIView, PaginationHandlerMixin):
    serializer_class = LocationZoneSerializer

    def get(self, request):
        location_zones = LocationZone.objects.filter(deleted_at=None)
        response = self.serializer_class(location_zones, many=True).data
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if request.user.role != 'admin':
            error_response = {
                "message": _("No tienes permisos para realizar esta acción"),
                "errors": [],
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            keys = request.data.keys()
            if not 'points' in keys:
                error_response = {
                    "message": _("Debes proporcionar los vértices de la zona"),
                    "errors": [],
                }
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
            points = request.data['points']

            if not len(points) > 2:
                error_response = {
                    "message": _("Debes proporcionar al menos 3 vértices de la zona"),
                    "errors": [],
                }
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

            location_zone = serializer.create(serializer.validated_data)

            try:
                for point in points:
                    location_zone_point = LocationZonePoint()
                    location_zone_point.location_zone = location_zone
                    location_zone_point.latitude = point['latitude']
                    location_zone_point.longitude = point['longitude']
                    location_zone_point.order = point['order']
                    location_zone_point.save()
            except:
                location_zone.delete()
                error_response = {
                    "message": _("Ocurrió un error al almacenar uno de los vértices de la zona"),
                    "errors": [],
                }
                return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

            response = self.serializer_class(location_zone).data
            return Response(response, status=status.HTTP_201_CREATED)
        error_response = {
            "message": _("Error al crear la zona"),
            "errors": serializer.errors,
        }
        return Response(error_response, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class LocationZoneView(APIView):
    serializer_class = LocationZoneSerializer

    def get(self, request, location_zone_pk):
        try:
            location_zone = LocationZone.objects.get(pk=location_zone_pk)
        except LocationZone.DoesNotExist:
            return Response(
                {"message": _("Zona no encontrada")},
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

    def put(self, request, location_zone_pk):
        try:
            location_zone = LocationZone.objects.get(pk=location_zone_pk)
        except LocationZone.DoesNotExist:
            return Response(
                {"message": _("Zona no encontrada")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.role == 'admin':
            if serializer.is_valid():
                location_zone = serializer.update(
                    location_zone, serializer.validated_data)
                serializer = self.serializer_class(location_zone)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        "message": _("Error al actualizar la zona"),
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"message": _("No tienes permisos para realizar está acción.")},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def delete(self, request, location_zone_pk):
        try:
            location_zone = LocationZone.objects.get(pk=location_zone_pk)
        except LocationZone.DoesNotExist:
            return Response(
                {"message": _("Zona no encontrada")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.role == 'admin':
            location_zone.deleted_at = datetime.now()
            location_zone.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"message": _("No tienes permisos para realizar está acción.")},
                status=status.HTTP_401_UNAUTHORIZED,
            )


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class LocationZoneUsersView(APIView):
    serializer_class = LocationZoneSerializer

    def get(self, request):
        if request.user.role != 'admin':
            return Response(
                {"message": _("No tienes permisos para realizar está acción.")},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        location_zones = LocationZone.objects.filter(
            deleted_at=None).order_by('name')
        zones_data = []

        for location_zone in location_zones:
            assignations = LocationAssignation.objects.filter(
                location_zone=location_zone, user__on_route=True)
            users = []
            for assignation in assignations:
                users.append(assignation.user)
            zones_data.append({
                'location_zone': self.serializer_class(location_zone).data,
                'users': UserActivitySerializer(users, many=True).data
            })

        return Response(zones_data, status=status.HTTP_200_OK)


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class LocationZonesPerifonView(APIView):
    serializer_class = LocationZoneSerializer

    def get(self, request):
        if request.user.role != 'admin':
            return Response(
                {"message": _("No tienes permisos para realizar está acción.")},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        location_zones = LocationZone.objects.filter(
            deleted_at=None).order_by('name')
        zones_data = []

        for location_zone in location_zones:

            points = LocationZonePoint.objects.filter(location_zone=location_zone)
            mapped_points = []
            for point in points:
                mapped_points.append([point.longitude, point.latitude])
            
            zones_data.append({
                'nombre_evento': None,
                'fecha_evento': None,
                'hora_ini_evento': None,
                'hora_fin_evento': None,
                'lugar_evento': None,
                'municipio': None,
                'localidad': None,
                'dl': None,
                'seccion': None,
                'campania_responsable': None,
                'descripcion': None,
                'requisitos': None,
                'responsable': None,
                'puesto_responsable': None,
                'celular1_responsable': None,
                'celular2_responsable': None,
                'contacto_seccion': None,
                'contacto_celular': None,
                'distrito': location_zone.name,
                'ubicacion': mapped_points
            })

        return Response(zones_data, status=status.HTTP_200_OK)
