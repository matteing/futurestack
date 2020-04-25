import uuid
from .models import User


def generate_test_users(count=2):
	users = []
	for i in range(count):
		user = User.objects.create_user(username=uuid.uuid4(), password="password")
		users.append(user)
	return users