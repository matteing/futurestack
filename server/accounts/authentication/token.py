from rest_framework.authentication import TokenAuthentication

# FUCK DAMN IT! THIS IS TERRIBLE!!!!
from accounts.timezone.utils import activate_user_timezone


class TokenAuthenticationWithTimezones(TokenAuthentication):

    def authenticate(self, request):
        user_auth_tuple = super().authenticate(request)

        if user_auth_tuple is None:
            return

        user, token = user_auth_tuple
        activate_user_timezone(request, user)
        return (user, token)