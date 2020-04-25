from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

from django.core.signing import TimestampSigner, BadSignature, SignatureExpired


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk)
            + six.text_type(timestamp)
            + six.text_type(user.is_active)
        )


account_activation_token = AccountActivationTokenGenerator()


class OneTimeToken:
    def __init__(self, user):
        self.user = user

    def make_token(self):
        return TimestampSigner().sign(self.user.username)

    @staticmethod
    def parse_token(token):
        return token.split(":")

    def check(self, token, max_age=60 * 60 * 48):
        try:
            data = TimestampSigner().unsign(token, max_age=max_age)
            return data == self.user.username
        except (BadSignature, SignatureExpired):
            return False

