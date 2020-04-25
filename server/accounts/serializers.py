import requests
from django.conf import settings
from rest_framework import serializers
import re
from .models import User
import django.contrib.auth.password_validation as validators


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)

    def validate_dark_mode(self, value):
        if self.instance and not self.instance.gold and value != False:
            raise serializers.ValidationError("You don't own hermes Gold.")
        return value

    def to_representation(self, instance):
        representation = super(UserSerializer, self).to_representation(instance)
        # Default to gravatar if no avatar is set.
        if not instance.avatar:
            representation['avatar'] = instance.gravatar()
        return representation

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'bio',
            'avatar',
            'timezone',
            'twitter',
            'github',
            'header',
            'is_staff',
            'telegram',
            'gold',
            'dark_mode',
        )
        read_only_fields = (
            'is_staff',
            'gold',
        )




class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class RegisterSerializer(serializers.Serializer):
    """
    Serializer for beta register endpoint.
    """
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    repeat_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    recaptcha_token = serializers.CharField(required=True)

    def validate_password(self, data):
        validators.validate_password(password=data, user=User)
        return data

    def validate(self, data):
        if not settings.SIGNUPS_OPEN:
            raise serializers.ValidationError("Makerlog is currently closed for signups. Contact @matteing on Twitter for access.")

        if not data.get('password') or not data.get('repeat_password'):
            raise serializers.ValidationError("Please enter a password and "
                                              "confirm it.")

        if data.get('password') != data.get('repeat_password'):
            raise serializers.ValidationError("Those passwords don't match.")

        # validate captcha
        if getattr(settings, 'RECAPTCHA_SECRET'):
            try:
                r = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
                    'secret': settings.RECAPTCHA_SECRET,
                    'response': data.get('recaptcha_token'),
                })
                if r.json()['success'] == False and not settings.DEBUG:
                    raise serializers.ValidationError("Incorrect ReCaptcha (Google says no).")
            except requests.exceptions.RequestException as e:
                raise serializers.ValidationError("Incorrect ReCaptcha (network error server-side).")

        return data

    def validate_email(self, email):
        existing = User.objects.filter(email=email).first()
        if existing:
            raise serializers.ValidationError("This email is already taken.")

        return email

    def validate_username(self, username):
        if not re.match(r'^\w+$', username):
            raise serializers.ValidationError("You can only use alphanumeric characters and underscores.")

        existing = User.objects.filter(username__iexact=username).first()
        if existing:
            raise serializers.ValidationError("This username is already taken.")

        return username.lower()


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        try:
            u = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("This email was not found.")

        return email