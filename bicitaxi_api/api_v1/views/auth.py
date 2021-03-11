from django.utils.translation import ugettext_lazy as _

from random import choice
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

from bicitaxi_api.api_v1.models import User, Profile
from bicitaxi_api.settings import URL_SERVER
from bicitaxi_api.api_v1.serializers.users import UserSerializer
from bicitaxi_api.api_v1.functions import send_email
from django.template.loader import render_to_string

# Create your views here.


class AuthView(APIView):
    """
    View for authenticate user
    """

    serializer_class = AuthTokenSerializer

    def post(self, request):
        """
        Method for obtain user token and user data
        :param request: Http request
        :return: The user data with token included
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, created = Token.objects.get_or_create(user=user)
            # We dont need do something with the token created, the serializers handle it
            user.profile = Profile.objects.get(user=user)
            response = UserSerializer(user).data
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {
                "message": _("Correo o contraseña incorrecta"),
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class LogoutView(APIView):
    """
    View for logout user
    """

    def post(self, request):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResetPasswordView(APIView):
    def post(self, request):
        try:
            email = request.data["email"]
            users = User.objects.filter(email=email)
            if len(users) == 0:
                return Response(
                    {"message": "Usuario no encontrado"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Create new password for the new user
            longitud = 8
            valores = (
                "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ<=>@#%&+"
            )

            p = ""
            password = p.join([choice(valores) for i in range(longitud)])

            user = users[0]
            user.set_password(password)
            user.save()

            content = render_to_string(
                "emails/password_reset.html", {"password": password}
            )
            send_email(
                "Nuevo contacto", content=content, to=[email], content_type="text/html"
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response(
                {"message": "Datos incompletos"}, status=status.HTTP_400_BAD_REQUEST
            )
