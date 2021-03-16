from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


class TelegramUserAuthentication(TokenAuthentication):
    keyword = 'Bot'
    
    def authenticate(self, request):
        token = super(TelegramUserAuthentication, self).authenticate(request)
        
        telegram_id = request.META.get('HTTP_TELEGRAM_ID', None)

        if not telegram_id:
            return None

        model = get_user_model()
        try:
            user = model.objects.get(telegram_id=telegram_id)
        except model.DoesNotExist:
            raise AuthenticationFailed(_('Invalid telegram_id.'))

        if not user.is_active:
            raise AuthenticationFailed(_('User inactive or deleted.'))

        return (user, token)

    def authenticate_credentials(self, key):
        if key != settings.TELEGRAM_BOT_TOKEN:
            raise AuthenticationFailed(_('Invalid token.'))
        return key


class TelegramBotAuthentication(TokenAuthentication):
    keyword = 'Bot'

    def authenticate_credentials(self, key):
        if key != settings.TELEGRAM_BOT_TOKEN:
            raise AuthenticationFailed(_('Invalid token.'))
        return (TelegramBot(), key)


class TelegramBot:
    is_active = True

    def __str__(self):
        return 'TelegramBot'

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True
