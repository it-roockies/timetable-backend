from django.contrib.auth import get_user_model

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from .serializers import UserSerializer
from .authentication import TelegramUserAuthentication, TelegramBotAuthentication


class TelegramUserViewSet(ViewSet):
    """Interacts with telegram user"""
    authentication_classes = [TelegramUserAuthentication]

    def create(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def list(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class TelegramBotViewSet(ViewSet):
    """Interacts with telegram user"""
    authentication_classes = [TelegramBotAuthentication]

    def create(self, request):
        telegram_id = request.data['telegram_id']
        username = request.data['username']
        email = request.data['email']

        model = get_user_model()
        try:
            user = model.objects.get(username=username, email=email)
        except model.DoesNotExist:
            raise AuthenticationFailed(_('Invalid user.'))

        if not user.is_active:
            raise AuthenticationFailed(_('User inactive or deleted.'))

        user.telegram_id = telegram_id
        user.save()

        serializer = self.get_serializer(request.user)
        return Response(serializer.data)