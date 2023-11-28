from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from auth.authentication import TokenHandler, TokenAuthenticationV2


class AuthViewsTestCase(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword',
            'email': 'test@example.com',
            'first_name': 'Lucho',
            'last_name': 'Corradini'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.client = APIClient()

    def test_login_status_200(self):
        login_data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post('/api/v1/auth/login/', login_data, format='json')

        token = Token.objects.first()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_expected = {
            "token": token and token.key or '',
            "user": {
                "username": "testuser",
                "email": "test@example.com",
                "first_name": "Lucho",
                "last_name": "Corradini"
            }
        }

        self.assertDictEqual(response.data, response_expected)

        token_key = response.data['token']
        token_exists = Token.objects.filter(key=token_key).exists()
        self.assertTrue(token_exists)

        token = Token.objects.get(key=token_key)
        self.assertIsNotNone(token.created)

        is_expired, _ = TokenHandler.expiration_handle(token)
        self.assertFalse(is_expired)

    def test_login_status_400_user_no_exists(self):
        login_data = {'username': 'testuser1', 'password': 'testpassword'}
        response = self.client.post('/api/v1/auth/login/', login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_expected = {
            "non_field_errors": [
                "Unable to log in with provided credentials."
            ]
        }

        self.assertEqual(response.data, response_expected)

        token_exists = Token.objects.filter().exists()
        self.assertFalse(token_exists)

    def test_login_status_400_without_params(self):
        login_data = {}
        response = self.client.post('/api/v1/auth/login/', login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_expected = {
            "username": [
                "This field is required."
            ],
            "password": [
                "This field is required."
            ]
        }

        self.assertEqual(response.data, response_expected)

        token_exists = Token.objects.filter().exists()
        self.assertFalse(token_exists)

    def test_logout_status_200(self):
        token = Token.objects.create(user=self.user)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.post('/api/v1/auth/logout/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_expected = {
            "message": "Logout successful"
        }

        self.assertEqual(response.data, response_expected)

        token_exists = Token.objects.filter(key=token.key, user=None).exists()
        self.assertFalse(token_exists)

        Token.objects.filter(key=token.key).delete()

    def test_logout_status_401_authentication_not_provider(self):
        token = Token.objects.create(user=self.user)

        response = self.client.post('/api/v1/auth/logout/', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response_expected = {
            "detail": "Authentication credentials were not provided."
        }

        self.assertEqual(response.data, response_expected)

        token_exists = Token.objects.filter(key=token.key).exists()
        self.assertTrue(token_exists)

        Token.objects.filter(key=token.key).delete()

    def test_logout_status_401_with_invalid_token(self):
        token = Token.objects.create(user=self.user)

        non_existent_token = 'b2facc0e0dc81603ba101201e85eea8483eb0dff'
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + non_existent_token)

        response = self.client.post('/api/v1/auth/logout/', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response_expected = {
            "detail": "Invalid token"
        }

        self.assertEqual(response.data, response_expected)

        token_exists = Token.objects.filter(key=token.key).exists()
        self.assertTrue(token_exists)

        token_exists = Token.objects.filter(key=non_existent_token).exists()
        self.assertFalse(token_exists)
    
    def test_register_status_201(self):
        user_data = {
            'username': 'testuser2',
            'password': 'testpassword',
            'password_confirmed': 'testpassword',
            'email': 'test2@example.com',
            'first_name': 'Lucho',
            'last_name': 'Corradini'
        }

        response = self.client.post('/api/v1/auth/register/', user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response_expected = {
            "username": "testuser2",
            "email": "test2@example.com",
            "first_name": "Lucho",
            "last_name": "Corradini"
        }

        self.assertEqual(response.data, response_expected)

        user_exists = User.objects.filter(username=response.data['username']).exists()
        self.assertTrue(user_exists)

    def test_register_status_400_username_already_exists(self):
        self.user_data['password_confirmed'] = 'testpassword'
        response = self.client.post('/api/v1/auth/register/', self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_expected = {
            "username": [
                "A user with that username already exists."
            ]
        }

        self.assertEqual(response.data, response_expected)

        user_exists = User.objects.filter(username=self.user_data['username']).exists()
        self.assertTrue(user_exists)

        all_users = User.objects.all().count()
        self.assertEqual(1, all_users)

    def test_register_status_400_without_body_params(self):
        users_before = User.objects.all().count()

        response = self.client.post('/api/v1/auth/register/', format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_expected = {
            "username": [
                "This field is required."
            ],
            "password": [
                "This field is required."
            ],
            "password_confirmed": [
                "This field is required."
            ],
            "email": [
                "This field is required."
            ],
            "first_name": [
                "This field is required."
            ],
            "last_name": [
                "This field is required."
            ]
        }

        self.assertDictEqual(response.data, response_expected)

        users_expected = User.objects.all().count()
        self.assertEqual(users_before, users_expected)

        user_exists = User.objects.filter(username=self.user.username).exists()
        self.assertTrue(user_exists)


class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        self.token = Token.objects.create(user=self.user)

    def test_token_handler_identifies_non_expired_token(self):
        is_expired, token = TokenHandler.expiration_handle(self.token)
        self.assertFalse(is_expired)

    def test_token_handler_identifies_expired_token(self):
        self.token.created = timezone.now() - timedelta(days=settings.TOKEN_EXPIRATION + 1)
        self.token.save()

        is_expired, token = TokenHandler.expiration_handle(self.token)
        self.assertTrue(is_expired)

    def test_token_handler_creates_new_token_on_login_if_expired(self):
        self.token.created = timezone.now() - timedelta(days=settings.TOKEN_EXPIRATION + 1)
        self.token.save()

        is_expired, token = TokenHandler.expiration_handle(self.token, is_login=True)
        self.assertFalse(is_expired)
        
        self.assertIsNotNone(token)
        self.assertNotEqual(token, self.token)
