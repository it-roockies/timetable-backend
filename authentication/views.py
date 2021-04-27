import json
from calendar import timegm
from cryptography.fernet import Fernet
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer

from django_otp import user_has_device
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp import devices_for_user

from .serializers import UserSerializer
from .authentication import TelegramUserAuthentication, TelegramBotAuthentication

def get_user_totp_device(self, user, confirmed=None):
    devices = devices_for_user(user, confirmed=confirmed)
    for device in devices:
        if isinstance(device, TOTPDevice):
            return device


class SessionPermission(BasePermission):
    """
    The request is authenticated as a user, or user can authenticate.
    """

    def has_permission(self, request, view):
        return bool(
            request.method == 'POST' or
            request.user and
            request.user.is_authenticated
        )

class SessionViewSet(ViewSet):
    permission_classes = (SessionPermission, )
    """Interacts with browser user"""
    def list(self, request):
        serializer = UserSerializer(request.user)
        return Response({"user": serializer.data})

    def create(self, request):
        serializer = AuthTokenSerializer(data=request.data, context={
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        })
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user_has_device(user, confirmed=True):
            msg = {'message': 'You have enabled two factor authentication.'}
            return Response(msg)
        user_serializer = UserSerializer(user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({"user": user_serializer.data, "token": token.key })


class TelegramUserViewSet(ViewSet):
    """Interacts with telegram user"""
    authentication_classes = (TelegramUserAuthentication, )

    def create(self, request):
        group = request.data.get('group')
        attended_questionnaire = request.data.get('attended_questionnaire')
        data = {
            "group": {"id": group},
            "attended_questionnaire": attended_questionnaire
        }
        serializer = UserSerializer(request.user, data=data, partial=True)
        print(serializer.is_valid())
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def list(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class TelegramBotViewSet(ViewSet):
    """Interacts with telegram user"""
    authentication_classes = (TelegramBotAuthentication, )

    def create(self, request):
        telegram_id = request.data.get('telegram_id')
        username = request.data.get('username')
        date_of_birth = request.data.get('date_of_birth')
        key = request.data.get('key')
        model = get_user_model()
        try:
            user = model.objects.get(username=username, telegram_id__isnull=True)
        except (model.DoesNotExist, ValidationError):
            raise AuthenticationFailed(_('Invalid user.'))
        if not user.date_of_birth:
            if key != '1':
                raise AuthenticationFailed(_('Invalid user!'))
            user.date_of_birth = date_of_birth
        if str(user.date_of_birth) != str(date_of_birth):
            raise AuthenticationFailed(_('Invalid user.'))
        if not user.is_active:
            raise AuthenticationFailed(_('User inactive or deleted.'))

        user.telegram_id = telegram_id
        user.save()

        serializer = UserSerializer(user)
        return Response(serializer.data)

class TimeLimitedQueryParamTokenViewSet(ViewSet):
    def create(self, request):
        if request.auth:
            token = request.auth.key
        else:
            token = Token.objects.get_or_create(user=request.user).key

        exp = timegm(datetime.utcnow().utctimetuple()) + settings.TOKEN_EXPIRATION_TIME

        payload = {
            "exp": exp,
            "token": token,
        }

        json_str = json.dumps(payload).encode("utf-8")

        cipher_suite = Fernet(settings.TOKEN_ENCRYPTION_KEY)
        query_param = cipher_suite.encrypt(json_str)

        return Response({"token": query_param})

class TOTPCreateView(ViewSet):

    def list(self, request):
        user = request.user
        device = get_user_totp_device(self, user=user)
        if not device:
            device = user.totpdevice_set.create(confirmed=False)
        url = device.config_url
        data = {'token': url}
        return Response(data, status=201)

class TOTPConfirmView(ViewSet):
    def create(self, request):
        user = request.user
        token = request.data.get('token')
        device = get_user_totp_device(self, user)
        if not device == None and device.verify_token(token):
            device.confirmed = True
            device.save()
            msg = {'success': 'Your device successfully confirmed'}
            return Response(msg)
        msg = {'error': 'Your token seems to be expired.'}
        return Response(msg)


class TOTPVerifyView(ViewSet):
    authentication_classes = []
    permission_classes = []
    def create(self, request):
        token = request.data.get('token', None)
        username = request.data.get('username', None)
        password = request.data.get('password', None)
        user = authenticate(username=username, password=password)
        if user is not None:
            device = get_user_totp_device(self, user)
            if not device == None and device.verify_token(token):
                if not device.confirmed:
                    msg = {'error': 'You have not yet confirmed your authenticator device.'}
                    return Response(msg)
                user_serializer = UserSerializer(user)
                token, created = Token.objects.get_or_create(user=user)
                return Response({"user": user_serializer.data, "token": token.key})
            return Response({"error": "Token does not exist or expired."})
        else:
            msg = {
                'error': 'Unable to authenticate with provided credentials'
            }
            return Response(msg)
