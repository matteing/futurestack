from djpaddle.models import Subscription
from rest_framework import serializers


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription

        fields = (
            "id",
            "status",
            "update_url",
            "cancel_url",
            "next_bill_date",
            "created_at",
        )
        read_only_fields = (
            "id",
            "status",
            "update_url",
            "cancel_url",
            "next_bill_date",
            "created_at",
        )
