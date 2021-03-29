import json
from calendar import timegm
from cryptography.fernet import Fernet, InvalidToken
from datetime import datetime
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


class TimeLimitedQueryParamTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        if 'token' not in request.query_params:
            raise AuthenticationFailed(_('Invalid token. No credentials provided.'))

        # Get token from request query params
        token = request.query_params.get('token').encode("utf-8")

        # Decrypt token
        cipher_suite = Fernet(settings.TOKEN_ENCRYPTION_KEY)
        try:
            json_str = cipher_suite.decrypt(token)
        except InvalidToken:
            raise AuthenticationFailed(_('Invalid token. Token should be encrypted data.'))

        # read json data
        try:
            payload = json.loads(json_str)
        except json.decoder.JSONDecodeError:
            raise AuthenticationFailed(_('Invalid token. Token should contain json data.'))

        # validate expiration time
        try:
            exp = int(payload["exp"])
        except ValueError:
            raise AuthenticationFailed(_('Invalid token. Expiration Time claim (exp) must be an integer.'))
        
        now = timegm(datetime.utcnow().utctimetuple())
        if exp < now:
            raise AuthenticationFailed(_("Invalid token. Token has expired."))

        return self.authenticate_credentials(payload["token"])


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
