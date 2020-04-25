from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from djpaddle.models import Subscription
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from billing.serializers import SubscriptionSerializer


class SubscriptionInfoView(APIView):
    def get(self, request):
        sub = Subscription.objects.filter(subscriber=request.user).filter(
            Q(status=Subscription.STATUS_ACTIVE)
            | Q(status=Subscription.STATUS_TRIALING)
            | Q(status=Subscription.STATUS_PAST_DUE)
            | Q(status=Subscription.STATUS_PAUSED)
        )
        if not sub.exists():
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        sub = sub.last()
        return Response(SubscriptionSerializer(sub).data)
