from copy import deepcopy
from unittest import mock

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from djpaddle.models import Subscription, Plan
from rest_framework.test import APITestCase

from accounts.models import User

FAKE_SUB_PAYLOAD = {
    "alert_id": 1,
    "alert_name": "subscription_created",
    "cancel_url": "https://checkout.paddle.com/subscription/cancel?user=1&subscription=2&hash=aaaaaa",
    "update_url": "https://checkout.paddle.com/subscription/update?user=5&subscription=4&hash=aaaaaa",
    "checkout_id": 1,
    "currency": "EUR",
    "email": "gardner.wuckert@example.org",
    "event_time": "2020-01-13 19:19:18",
    "marketing_consent": 1,
    "next_bill_date": "2020-01-30",
    "passthrough": "",
    "quantity": 1,
    "source": "",
    "status": "active",
    "subscription_id": 1,
    "subscription_plan_id": 1,
    "unit_price": 0,
    "user_id": 1,
}


class SubStatusTestCase(APITestCase):
    fixtures = ["users"]

    def setUp(self):
        plan = Plan.objects.create(
            pk=1,
            name="monthly-subscription",
            billing_type="month",
            billing_period=1,
            trial_days=0,
        )

    @mock.patch("djpaddle.views.is_valid_webhook", return_value=True)
    def test_sub_created_turns_on_gold(self, is_valid_webhook):
        """ Test whether creating an active subscription turns on Gold for the user. """
        user = User.objects.first()
        PAYLOAD = deepcopy(FAKE_SUB_PAYLOAD)
        PAYLOAD["email"] = user.email
        PAYLOAD["p_signature"] = "valid-signature"
        res = self.client.post(reverse("djpaddle:webhook"), data=PAYLOAD)
        user.refresh_from_db()
        self.assertEquals(res.status_code, 200)
        self.assertEquals(user.gold, True)
        # self.assertEquals(len(mail.outbox), 1)
        # self.assertIn("Gold", mail.outbox[0].body)

    @mock.patch("djpaddle.views.is_valid_webhook", return_value=True)
    def test_sub_deleted_turns_off_gold(self, is_valid_webhook):
        """ Test whether deleting an active subscription turns off Gold for the user. """
        user = User.objects.first()
        PAYLOAD = deepcopy(FAKE_SUB_PAYLOAD)
        PAYLOAD["email"] = user.email
        PAYLOAD["alert_name"] = "subscription_cancelled"
        PAYLOAD["status"] = "paused"
        res = self.client.post(reverse("djpaddle:webhook"), data=PAYLOAD)
        user.refresh_from_db()
        self.assertEquals(res.status_code, 200)
        self.assertEquals(user.gold, False)
