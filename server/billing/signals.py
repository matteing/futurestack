import sys

from django.db.models.signals import post_save
from django.dispatch import receiver
from djpaddle.models import Subscription

from accounts.models import User
from billing.utils import is_sub_active


@receiver(post_save, sender=Subscription)
def on_subscription_update(sender, instance, *args, **kwargs):
    user = instance.subscriber
    if not user or not isinstance(user, User):
        return

    if (
        is_sub_active(instance)
        and kwargs["created"]
        and (not sys.argv[0] == "manage.py" or "test" in sys.argv)
    ):
        pass
        # do whatever you do when a new sub is created

    if user.gold != is_sub_active(instance):
        user.gold = is_sub_active(instance)
        user.save()
