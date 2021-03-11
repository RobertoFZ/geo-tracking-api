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

from bicitaxi_api.api_v1.models import LocationZone, LocationZonePoint
from bicitaxi_api.common.pagination import PaginationHandlerMixin
from bicitaxi_api.settings import URL_SERVER
from bicitaxi_api.api_v1.raycasting import Raycasting


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class InsideValidationView(APIView, PaginationHandlerMixin):

    def post(self, request):
        keys = request.data.keys()

        if not 'location_zone_id' in keys or not 'point' in keys:
            error_response = {
                "message": _("Debes indicar el ID de la zona y la coordenada a validar"),
                "errors": [],
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

        location_zone = None
        location_zone_id = request.data['location_zone_id']
        point = request.data['point']
        try:
            location_zone = LocationZone.objects.get(id=location_zone_id)
        except LocationZone.DoesNotExist:
            error_response = {
                "message": _("No se encontró la zona indicada"),
                "errors": [],
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

        location_zone_points = LocationZonePoint.objects.filter(location_zone=location_zone)
        polygon_points = []

        for location_point in location_zone_points:
            polygon_points.append("%s,%s" % (location_point.latitude, location_point.longitude))

        try:
            register_point = "%s,%s" % (point['latitude'], point['longitude'])
        except:
            error_response = {
                "message": _("La coordenada indicada es inválida"),
                "errors": [],
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

        # We use raycasting algorithm to validate the point inside the Geofence
        rayCasting = Raycasting(polygon_points, register_point)
        rayCasting.polypp()

        is_inside = False
        if rayCasting.ispointinside():
            is_inside = True
        response = {
            'is_inside': is_inside
        }
        return Response(response, status=status.HTTP_200_OK)
