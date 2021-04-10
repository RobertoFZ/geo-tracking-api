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

from bicitaxi_api.api_v1.models import User, Location, Profile, LocationAssignation, LocationZone
from bicitaxi_api.common.pagination import PaginationHandlerMixin
from bicitaxi_api.settings import URL_SERVER
from bicitaxi_api.api_v1.serializers.locations import LocationSerializer
from bicitaxi_api.api_v1.serializers.location_zones import LocationZoneSerializer
from bicitaxi_api.api_v1.serializers.users import UserSerializer, UserSimpleSerializer
from bicitaxi_api.api_v1.functions import distance_between_two_points
from bicitaxi_api.api_v1.serializers.reports import ReportSerializer


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class ReportView(APIView, PaginationHandlerMixin):
    serializer_class = ReportSerializer
    pagination_class = LimitOffsetPagination

    def post(self, request):
        params = request.query_params.keys()
        keys = request.data.keys()

        if not 'from' in keys or not 'to' in keys:
            error_response = {
                "message": _("Se debe indicar los valores 'from' y 'to' para hacer el filtrado por fecha"),
                "errors": [],
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        if not 'zone_id' in keys:
            error_response = {
                "message": _("Se debe indicar el ID de la zona para generar el reporte"),
                "errors": [],
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        location_zone = None
        try:
            location_zone = LocationZone.objects.get(
                pk=request.data['zone_id'])
        except LocationZone.DoesNotExist:
            error_response = {
                "message": _("La zona indicada no es válida"),
                "errors": [],
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        start_date_string = request.data['from']
        end_date_string = request.data['to']

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
        zone_assignations = LocationAssignation.objects.filter(
            location_zone=location_zone, user__role='driver')
        users = []

        for assignation in zone_assignations:
            users.append(assignation.user)

        user_data = []
        for user in users:
            registers = []
            locations = Location.objects.filter(
                user=user,
                date__range=[start_date, end_date]
            ).order_by('date')
            time = 0.0
            distance = 0.0
            last_register = None
            is_same_day = False
            for register in locations:
                print(register.date)
                if last_register and ((register.date.hour > 7 and register.date.hour <= 14) or (register.date.hour > 14 and register.date.hour <= 23)):
                    is_same_day = last_register.date.day == register.date.day

                    diff = register.date - last_register.date

                    days, seconds = diff.days, diff.seconds
                    hours = days * 24 + seconds // 3600
                    minutes = (seconds % 3600) // 60
                    seconds = seconds % 60

                    if is_same_day:
                        time += minutes
                        # Calculate distance
                        distance += distance_between_two_points(
                            last_register, register)
                        # if distance < .03 and len(registers) > 0:
                        #    registers[len(registers) - 1].date = register.date
                        # else:
                        #    registers.append(register)
                    registers.append(register)

                last_register = register
            user.profile = Profile.objects.get(user=user)
            user_data.append({
                'locations': LocationSerializer(registers, many=True).data,
                'location_zone': LocationZoneSerializer(location_zone).data,
                'user': UserSimpleSerializer(user).data,
                'start_date': start_date,
                'end_date': end_date,
                'time': time,
                'distance': distance
            })

        page = self.paginate_queryset(user_data)
        if page is not None and 'limit' in params:
            response = self.get_paginated_response(page).data
        else:
            response = user_data
        return Response(response, status=status.HTTP_200_OK)
