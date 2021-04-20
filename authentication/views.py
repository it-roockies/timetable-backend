import json
from calendar import timegm
from cryptography.fernet import Fernet
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer

from .serializers import UserSerializer
from .authentication import TelegramUserAuthentication, TelegramBotAuthentication


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
        user_serializer = UserSerializer(user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({"user": user_serializer.data, "token": token.key })


class TelegramUserViewSet(ViewSet):
    """Interacts with telegram user"""
    authentication_classes = (TelegramUserAuthentication, )

    def create(self, request):
        print(request.data)
        serializer = UserSerializer(request.user, data=request.data, partial=True)
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