# -*- coding: utf-8 -*-
#
import traceback

from django.contrib.auth import get_user_model
from radiusauth.backends import RADIUSBackend, RADIUSRealmBackend
from django.conf import settings


User = get_user_model()


class CreateUserMixin:
    def get_django_user(self, username, password=None, *args, **kwargs):
        if isinstance(username, bytes):
            username = username.decode()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            if '@' in username:
                email = username
            else:
                email_suffix = settings.EMAIL_SUFFIX
                email = '{}@{}'.format(username, email_suffix)
            user = User(username=username, name=username, email=email)
            user.source = user.Source.radius.value
            user.save()
        return user

    def _perform_radius_auth(self, client, packet):
        # TODO: 等待官方库修复这个BUG
        try:
            return super()._perform_radius_auth(client, packet)
        except UnicodeError as e:
            import sys
            tb = ''.join(traceback.format_exception(*sys.exc_info(), limit=2, chain=False))
            if tb.find("cl.decode") != -1:
                return [], False, False
            return None


class RadiusBackend(CreateUserMixin, RADIUSBackend):
    def authenticate(self, request, username='', password='', **kwargs):
        return super().authenticate(request, username=username, password=password)


class RadiusRealmBackend(CreateUserMixin, RADIUSRealmBackend):
    def authenticate(self, request, username='', password='', realm=None, **kwargs):
        return super().authenticate(request, username=username, password=password, realm=realm)
