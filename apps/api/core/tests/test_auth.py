import os

import pytest
from rest_framework import status
from rest_framework.test import APIClient

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

import django

django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

REGISTER_ENDPOINT = "/api/auth/register/"
LOGIN_ENDPOINT = "/api/auth/login/"
LOGOUT_ENDPOINT = "/api/auth/logout/"
ME_ENDPOINT = "/api/auth/me/"

pytestmark = pytest.mark.django_db


class TestRegister:
    def test_given_valid_payload_when_register_then_creates_user_and_returns_token(self):
        api_client = APIClient()
        payload = {"name": "Beatriz", "email": "Beatriz@Example.com", "password": "uma-senha-forte-123"}

        response = api_client.post(REGISTER_ENDPOINT, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["token"]
        assert data["user"]["email"] == "beatriz@example.com"
        assert data["user"]["name"] == "Beatriz"

        # username e email sao gravados normalizados (lowercase) e o token persiste.
        user = User.objects.get(email="beatriz@example.com")
        assert user.username == "beatriz@example.com"
        assert Token.objects.filter(user=user).exists()

    def test_given_duplicate_email_when_register_then_returns_400(self):
        User.objects.create_user(username="taken@example.com", email="taken@example.com", password="abc12345xyz")
        api_client = APIClient()
        payload = {"email": "taken@example.com", "password": "outra-senha-456"}

        response = api_client.post(REGISTER_ENDPOINT, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.json()

    def test_given_weak_password_when_register_then_returns_400(self):
        api_client = APIClient()
        payload = {"email": "novo@example.com", "password": "123"}

        response = api_client.post(REGISTER_ENDPOINT, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.json()


class TestLogin:
    def test_given_valid_credentials_when_login_then_returns_token(self):
        User.objects.create_user(username="ana@example.com", email="ana@example.com", password="senha-correta-789")
        api_client = APIClient()
        payload = {"email": "ana@example.com", "password": "senha-correta-789"}

        response = api_client.post(LOGIN_ENDPOINT, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["token"]

    def test_given_wrong_password_when_login_then_returns_401(self):
        User.objects.create_user(username="ana@example.com", email="ana@example.com", password="senha-correta-789")
        api_client = APIClient()
        payload = {"email": "ana@example.com", "password": "senha-errada"}

        response = api_client.post(LOGIN_ENDPOINT, payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserMeAndLogout:
    def _auth_client(self, email: str = "user@example.com", password: str = "senha-do-user-321") -> tuple[APIClient, Token]:
        user = User.objects.create_user(username=email, email=email, password=password, first_name="User")
        token = Token.objects.create(user=user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        return client, token

    def test_given_no_token_when_get_me_then_returns_401(self):
        response = APIClient().get(ME_ENDPOINT)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_given_token_when_get_me_then_returns_profile(self):
        client, _ = self._auth_client()

        response = client.get(ME_ENDPOINT)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == "user@example.com"

    def test_given_token_when_logout_then_revokes_token(self):
        client, token = self._auth_client()

        response = client.post(LOGOUT_ENDPOINT)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Token.objects.filter(key=token.key).exists()
