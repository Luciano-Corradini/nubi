from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from datetime import timedelta
from django.utils import timezone
from django.conf import settings


class TokenHandler:
    """
    If token is expired then it will be removed
    """

    @classmethod
    def expiration_handle(cls, token, is_login=False):
        time_elapsed = timezone.now() - token.created
        left_time = timedelta(days = settings.TOKEN_EXPIRATION) - time_elapsed
        is_expired = left_time < timedelta(seconds = 0)

        if is_login:
            token.delete()
            token = Token.objects.create(user = token.user)
            return False, token

        return is_expired, token


class TokenAuthenticationV2(TokenAuthentication):
    """
    This version includes an expiration handler to achieve an additional level of security
    """

    def authenticate_credentials(self, key):
        try:
            token = Token.objects.get(key = key)
        except Token.DoesNotExist:
            raise AuthenticationFailed("Invalid token")
        
        if not token.user.is_active:
            raise AuthenticationFailed("User inactive or deleted")

        is_expired, token = TokenHandler.expiration_handle(token)
        if is_expired:
            raise AuthenticationFailed("Expired Token")
        
        return (token.user, token)
