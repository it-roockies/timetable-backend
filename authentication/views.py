import json
from calendar import timegm
from cryptography.fernet import Fernet
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer
from .authentication import TelegramUserAuthentication, TelegramBotAuthentication

class SessionViewSet(ViewSet):
    """Interacts with browser user"""
    def list(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class TelegramUserViewSet(ViewSet):
    """Interacts with telegram user"""
    authentication_classes = [TelegramUserAuthentication]

    def create(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def list(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class TelegramBotViewSet(ViewSet):
    """Interacts with telegram user"""
    authentication_classes = [TelegramBotAuthentication]

    def create(self, request):
        telegram_id = request.data['telegram_id']
        username = request.data['username']
        date_of_birth = request.data['date_of_birth']

        model = get_user_model()
        try:
            user = model.objects.get(username=username, date_of_birth=date_of_birth, telegram_id__isnull=True)
        except model.DoesNotExist:
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