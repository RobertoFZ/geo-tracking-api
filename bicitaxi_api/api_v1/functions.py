import traceback
import random
import string

import sys
from django.core.mail import EmailMultiAlternatives
from math import sin, cos, sqrt, atan2, radians


def send_email(subject, content, to, content_type="text/plain"):
    """
    Envía un email con el contenido que se le designe.
    :param subject: Título del email.
    :param content: contenido o body del mensaje.
    :param content_type: tipo de contenido Ej. "text/plain"
    :param to: lista de usuarios a los que llegará el email.
    :return: True o False para confirmar el envío.
    """
    try:
        msg = EmailMultiAlternatives(subject=subject, body=content, to=to)
        if content_type == "text/html":
            msg.attach_alternative(content, "text/html")
        msg.send()
    except:
        message = format_sys_errors(sys, with_traceback=True)
        print(message)


def format_sys_errors(user_sys, with_traceback=False):
    if user_sys:
        etype, value, tb = user_sys.exc_info()
        tipo_error_name = etype.__name__
        error_args = value.args
        if with_traceback:
            mensaje = "{0} {1} {2}".format(
                tipo_error_name, error_args, traceback.extract_tb(tb))
        else:
            traceback.print_tb(tb)
            mensaje = "{0} {1}".format(tipo_error_name, error_args)
        return mensaje
    else:
        return ""


def generateOrderString(sufix='', stringLength=10):
    letters = string.ascii_lowercase
    randomOrderString = ''.join(random.choice(letters)
                                for i in range(stringLength))
    return "%s-%s" % (sufix, randomOrderString)


def distance_between_two_points(point_one, point_two):
    # approximate radius of earth in km
    r = 6373.0

    lat1 = radians(float(point_one.latitude))
    lon1 = radians(float(point_one.longitude))
    lat2 = radians(float(point_two.latitude))
    lon2 = radians(float(point_two.longitude))

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return round(r * c, 2)
