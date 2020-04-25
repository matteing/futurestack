from djpaddle.models import Subscription


def is_sub_active(subscription):
    return (
        subscription.status == Subscription.STATUS_ACTIVE
        or subscription.status == Subscription.STATUS_TRIALING
    )
