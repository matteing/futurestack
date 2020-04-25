import base64
import collections
import copy
import json
import os
import re
import urllib
from datetime import timedelta

import django.contrib.auth.password_validation as validators
import phpserialize
import pytz
import requests
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core import exceptions
from django.core.mail import send_mail
from django.db.models import Count, F, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.safestring import mark_safe
from ipware import get_client_ip
from rest_framework import permissions, serializers, status
from rest_framework import viewsets, generics, pagination
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import UpdateAPIView, CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import User
from accounts.permissions import IsUserOrReadOnly, UnauthenticatedOnly
from accounts.tokens import account_activation_token
from accounts.tokens import OneTimeToken
from .serializers import (
    UserSerializer,
    ChangePasswordSerializer,
    RegisterSerializer,
    PasswordResetRequestSerializer,
)

DIR_PATH = os.path.dirname(os.path.realpath(__file__))


class UsersViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAdminUser,)
    permission_classes = (IsUserOrReadOnly,)
    serializer_class = UserSerializer
    pagination_class = pagination.LimitOffsetPagination
    default_limit = 10
    lookup_field = "username"
    queryset = User.objects.all()


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class TimezoneView(APIView):
    def post(self, request, format=None):
        if request.data.get("timezone") in pytz.all_timezones:
            # cant use sessions cause SPA uses token
            if request.user.timezone != request.data.get("timezone"):
                request.user.timezone = request.data.get("timezone")
                request.user.save()
            return Response({"success": True})
        else:
            return Response(
                {"success": False, "message": "Invalid timezone.",},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ChangePasswordView(UpdateAPIView):
    """
    An endpoint for changing password.
    """

    serializer_class = ChangePasswordSerializer
    model = User

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response({"success": True}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(CreateAPIView):
    """
    Beta register endpoint.
    """

    serializer_class = RegisterSerializer
    queryset = User.objects.all()
    permission_classes = (UnauthenticatedOnly,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(
            email=serializer.validated_data["email"],
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
            is_active=False,
        )

        uidb64 = urllib.parse.quote(urlsafe_base64_encode(force_bytes(user.pk)))
        token = urllib.parse.quote(account_activation_token.make_token(user))
        # Send activation email.a
        app_name = getattr(settings, "PROJECT_NAME", "New App")
        confirm_url = mark_safe(
            "%s/begin?uid=%s&token=%s" % (settings.FRONTEND_ROOT, uidb64, token)
        )
        msg_plain = render_to_string(
            "emails/confirm_email.txt",
            {"confirm_url": confirm_url, "app_name": app_name},
        )
        msg_html = render_to_string(
            "emails/confirm_email.html",
            {"confirm_url": confirm_url, "app_name": app_name},
        )
        send_mail(
            "%s: Confirm your email" % app_name,
            msg_plain,
            "%s <%s>" % (app_name, settings.DEFAULT_FROM_EMAIL),
            [user.email],
            html_message=msg_html,
        )
        return Response(
            {"success": True, "message": "Account created."},
            status=status.HTTP_201_CREATED,
        )


class ActivationView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, uid, token, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user != None and account_activation_token.check_token(user, token):
            user.is_active = True
            client_ip, is_routable = get_client_ip(request)
            if client_ip:
                user.last_ip = client_ip
            user.save()
            token, created = Token.objects.get_or_create(user=user)

            return Response({"token": token.key,})
        else:
            return Response({"success": False})


class PasswordResetRequestView(CreateAPIView):
    permission_classes = (UnauthenticatedOnly,)
    serializer_class = PasswordResetRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=serializer.validated_data["email"])
        # Make that email
        app_name = getattr(settings, "PROJECT_NAME", "New App")
        token = urllib.parse.quote(default_token_generator.make_token(user))
        uid = urllib.parse.quote(urlsafe_base64_encode(force_bytes(user.pk)))
        reset_url = mark_safe(
            "%s/forgot?token=%s&uid=%s" % (settings.FRONTEND_ROOT, token, uid)
        )
        msg_plain = render_to_string(
            "emails/reset_password.txt",
            {"reset_url": reset_url, "user": user, "app_name": app_name},
        )
        msg_html = render_to_string(
            "emails/reset_password.html",
            {"reset_url": reset_url, "user": user, "app_name": app_name},
        )
        send_mail(
            "%s: Password reset requested" % app_name,
            msg_plain,
            "%s <%s>" % (app_name, settings.DEFAULT_FROM_EMAIL),
            [user.email],
            html_message=msg_html,
        )
        return Response(
            {"success": True, "message": "Email sent."}, status=status.HTTP_200_OK
        )


class PasswordResetSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(min_length=6)
    repeat_password = serializers.CharField(min_length=6)

    def validate_uidb64(self, uidb64):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise ValidationError("User not found or invalid base64.")

        return uid

    def validate(self, data):
        password = data.get("password")

        errors = dict()
        try:
            # validate the password and catch the exception
            validators.validate_password(password=password, user=User)
            if password != data.get("repeat_password"):
                raise ValidationError("Passwords do not match.")
        # the exception raised here is different than serializers.ValidationError
        except exceptions.ValidationError as e:
            errors["password"] = list(e.messages)

        if not default_token_generator.check_token(
            User.objects.get(pk=data.get("uidb64")), data.get("token")
        ):
            errors["token"] = "Invalid token."

        if errors:
            raise serializers.ValidationError(errors)

        return super(PasswordResetSerializer, self).validate(data)


class PasswordResetView(CreateAPIView):
    permission_classes = (UnauthenticatedOnly,)
    serializer_class = PasswordResetSerializer

    def create(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(pk=serializer.validated_data.get("uidb64"))
        user.set_password(serializer.validated_data.get("password"))
        user.save()
        return Response(
            {"success": True, "message": "Password changed."}, status=status.HTTP_200_OK
        )


class UnsubscribeView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        if not request.GET.get("token") or not request.GET.get("username"):
            return Response("Missing field.", status=status.HTTP_400_BAD_REQUEST)
        token_string = urllib.parse.unquote(request.GET.get("token"))
        username = urllib.parse.unquote(request.GET.get("username"))
        try:
            user = User.objects.get(username=username)
            ott = OneTimeToken(user)
            if ott.check(token_string):
                user.newsletter = False
                user.save()
                return Response("Unsubscribed. :(", status=status.HTTP_200_OK)
            else:
                return Response(
                    "Invalid signature.", status=status.HTTP_400_BAD_REQUEST
                )
        except User.DoesNotExist:
            return Response(
                "Invalid signature. (2)", status=status.HTTP_400_BAD_REQUEST
            )


class MentionRedirect(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, username=None):
        return redirect("user-detail", username=username)
