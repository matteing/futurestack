from hashlib import md5

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
	bio = models.TextField(blank=True, null=True)
	timezone = models.CharField(blank=True, null=True, max_length=140)
	avatar = models.ImageField(upload_to='uploads/avatars/%Y/%m/%d/', blank=True)
	header = models.ImageField(upload_to='uploads/headers/%Y/%m/%d/', blank=True)

	# Emails
	newsletters = models.BooleanField(default=False)

    # Paid features
	gold = models.BooleanField(default=False)
	dark_mode = models.BooleanField(default=False)

    # Social handles
	twitter = models.CharField(blank=True, null=True, max_length=140)
	telegram = models.CharField(blank=True, null=True, max_length=140)
	github = models.CharField(blank=True, null=True, max_length=140)

	# Security
	last_ip = models.GenericIPAddressField(blank=True, null=True)


	def gravatar(self, default='mm', size='150', rating='pg'):
		""" Retrieve an avatar url from gravatar.com for the user instance. """
		email = self.email
		email_hash = md5(email.encode('utf-8')).hexdigest()
		url = "https://gravatar.com/avatar/%s?s=%s&d=%s&r=%s" % (
			email_hash, size, default, rating)
		return url

	def avatar_or_gravatar(self):
		if not self.avatar:
			return self.gravatar()
		else:
			return self.avatar.url