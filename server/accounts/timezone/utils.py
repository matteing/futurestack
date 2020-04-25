import pytz
from django.utils import timezone


def activate_user_timezone(request, user=None):
    header_timezone = request.META.get('HTTP_X_APP_TIMEZONE', False)
    user_timezone = None
    if not user:
        user = request.user

    if user.is_authenticated:
        user_timezone = user.timezone

    try:
        if header_timezone:
            timezone.activate(pytz.timezone(header_timezone))
        elif user_timezone:
            timezone.activate(pytz.timezone(user_timezone))
        else:
            timezone.deactivate()
    except:
        timezone.deactivate()