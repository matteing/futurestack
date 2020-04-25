from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

from .views import MeView, TimezoneView, \
    ChangePasswordView, RegisterView, ActivationView, PasswordResetRequestView, PasswordResetView

app_name = 'accounts'

urlpatterns = [
	path('me/', MeView.as_view(), name="me"),
    path('me/set_timezone', TimezoneView.as_view(), name="set-timezone"),
    path('accounts/activate/<str:uid>/<str:token>/', ActivationView.as_view(), name="activate"),
    path('accounts/forgot/', PasswordResetRequestView.as_view(), name="forgot"),
    path('accounts/reset/', PasswordResetView.as_view(), name="reset"),
    path('accounts/change_password/', ChangePasswordView.as_view(), name="change-password"),
    path('accounts/register/', RegisterView.as_view(), name='register'),
]

auth_patterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', obtain_auth_token),
]