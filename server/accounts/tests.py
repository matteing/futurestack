from hashlib import md5
from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.decorators import anonymous_required
from accounts.serializers import UserSerializer
from .models import User

class AuthedTestCase(APITestCase):
	fixtures = ['users']

	def assertGuestFails(self, urls):
		for url in urls:
			response = self.client.get(url, format='json')
			self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TestMeView(AuthedTestCase):
	def test_me_returns_user(self):
		"""
		Uhh. Tests whether /me/ works properly.
		"""
		user = User.objects.get(username='test1')
		self.client.login(username='test1', password='testing')
		url = reverse('accounts:me')
		resp = self.client.get(url)
		self.assertEquals(resp.json(), UserSerializer(user).data)

class TestChangePasswordEndpoint(AuthedTestCase):
	base_url = reverse('accounts:change-password')

	def test_permissions(self):
		"""
		Verifies whether permissions for this endpoint are correct.
		"""
		self.assertGuestFails([
			self.base_url
		])

	def test_change_password_works(self):
		"""
		Test whether this endpoint changes password.
		"""
		user = User.objects.last()
		initial_password = 'initial_password'
		new_password = 'new_password'
		user.set_password(initial_password)
		user.save()
		self.client.login(username=user.username, password=initial_password)
		resp = self.client.put(
			self.base_url,
			{
				'old_password': initial_password,
				'new_password': new_password
			}
		)
		self.assertEquals(resp.status_code, 200)
		self.assertEquals(resp.json()['success'], True)
		# Now verify (refresh user obj)
		user = User.objects.last()
		self.assertTrue(user.check_password(new_password))
		self.assertFalse(user.check_password(initial_password))

	def test_change_password_rejects_wrong(self):
		"""
		Test whether this endpoint rejects wrong passwords.
		"""
		# Try wrong old password.
		# Check if no change afterwards.
		user = User.objects.last()
		initial_password = 'initial_password'
		new_password = 'new_password'
		user.set_password(initial_password)
		user.save()
		self.client.login(username=user.username, password=initial_password)
		resp = self.client.put(
			self.base_url,
			{
				'old_password': new_password,
				'new_password': initial_password
			}
		)
		self.assertEquals(resp.status_code, 400)
		# Now verify (refresh user obj)
		user = User.objects.last()
		self.assertTrue(user.check_password(initial_password))
		self.assertFalse(user.check_password(new_password))

	def test_wrong_input(self):
		"""
		Test wrong type passed to serializer.
		"""
		user = User.objects.last()
		initial_password = 'initial_password'
		new_password = 'new_password'
		user.set_password(initial_password)
		user.save()
		self.client.login(username=user.username, password=initial_password)
		resp = self.client.put(
			self.base_url,
			{
				'old_password': [],
				'new_password': []
			}
		)
		self.assertEquals(resp.status_code, 400)

class TestTimezones(AuthedTestCase):
	def test_authorized(self):
		url = reverse('accounts:set-timezone')
		self.assertGuestFails([url])

	def test_trash_timezone(self):
		"""
		Test setting a fake timezone.
		"""
		self.client.login(username='test1', password='testing')
		url = reverse('accounts:set-timezone')
		payload = dict(timezone="trash/trash")
		resp = self.client.post(url, payload, format='json')
		self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

	def test_good_timezone(self):
		"""
		Test setting a good timezone.
		"""
		self.client.login(username='test1', password='testing')
		url = reverse('accounts:set-timezone')
		payload = dict(timezone="America/Puerto_Rico")
		resp = self.client.post(url, payload, format='json')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)

class TestAccessDecorators(APITestCase):
	fixtures = ['users']

	def test_anonymous_required(self):
		"""
		Test whether anonymous_required decorator and class works properly.
		"""
		request = mock.MagicMock()
		# Set the required properties of your request
		function = lambda x: x
		decorator = anonymous_required(function)
		response = decorator(request)
		self.assertEquals(response.status_code, 302)

class TestUserModelMethods(APITestCase):
	fixtures = ['users']

	def test_gravatar_support(self):
		user = User.objects.first()
		email_hash = md5(user.email.encode('utf-8')).hexdigest()
		gravatar = user.gravatar()
		self.assertIsInstance(gravatar, str)
		self.assertEquals(
			True,
			email_hash in gravatar
		)

class TestUserSerializer(APITestCase):
	fixtures = ['users']

	def setUp(self):
		self.user = User.objects.first()
		Task.objects.create(
			done=True,
			content="Test",
			user=self.user,
		)
		self.serializer = UserSerializer(self.user)

class TestRegisterView(AuthedTestCase):
	fixtures = ['users.json']

	def test_creates_user(self):
		"""
		Test whether register creates a user.
		"""
		email = 'test@testing123.com'
		username = 'test_creates_user'
		password = 'password2423'
		with self.settings(DEBUG=True):
			resp = self.client.post(
				reverse('accounts:register'),
				{
					'email': email,
					'username': username,
					'repeat_password': password,
					'password': password,
					'recaptcha_token': 'testing',
				}
			)
			self.assertEquals(resp.status_code, 201)
			self.assertTrue(User.objects.filter(username=username).exists())

	def test_validates_repeat(self):
		"""
		Tests whether register validates repeat passwords.
		"""
		email = 'test@testing123.com'
		username = 'test_creates_user'
		password = 'password2423'
		with self.settings(RECAPTCHA_TOKEN=None):
			resp = self.client.post(
				reverse('accounts:register'),
				{
					'email': email,
					'username': username,
					'password': password,
					'recaptcha_token': 'testing',
				}
			)
			self.assertEquals(resp.status_code, 400)

	def test_validates_email_taken(self):
		"""
		Tests whether register validates taken emails.
		"""
		email = 'test@tessdsting123.com'
		username = 'test_creates_user'
		password = 'password2423'
		User.objects.create_user(
			email=email,
			username=username,
			password=password
		)
		with self.settings(RECAPTCHA_TOKEN=None):
			resp = self.client.post(
				reverse('accounts:register'),
				{
					'email': email,
					'username': "different_user",
					'password': password,
					'recaptcha_token': 'testing',
				}
			)
			self.assertEquals(resp.status_code, 400)
			self.assertContains(resp, 'taken', status_code=400)

	def test_validates_username_taken(self):
		"""
		Tests whether register validates taken username.
		"""
		email = 'test@tessdsting123.com'
		username = 'test_creates_user'
		password = 'password2423'
		User.objects.create_user(
			email=email,
			username=username,
			password=password
		)
		with self.settings(RECAPTCHA_TOKEN=None):
			resp = self.client.post(
				reverse('accounts:register'),
				{
					'email': "different@email.com",
					'username': username,
					'password': password,
					'recaptcha_token': 'testing',
				}
			)
			self.assertEquals(resp.status_code, 400)
			self.assertContains(resp, 'taken', status_code=400)

	def test_validates_username_non_alphanumeric(self):
		"""
		Tests whether register validates username format.
		"""
		email = 'test@tessdsting123.com'
		username = '%3jwhello'
		password = 'password2423'
		User.objects.create_user(
			email=email,
			username=username,
			password=password
		)
		with self.settings(RECAPTCHA_TOKEN=None):
			resp = self.client.post(
				reverse('accounts:register'),
				{
					'email': "different@email.com",
					'username': username,
					'password': password,
					'recaptcha_token': 'testing',
				}
			)
			self.assertEquals(resp.status_code, 400)
			self.assertContains(resp, 'alphanumeric', status_code=400)