from django.urls import path, include

from billing.views import SubscriptionInfoView

app_name = "billing"

urlpatterns = [
    path("subscription/", SubscriptionInfoView.as_view(), name="info"),
]
