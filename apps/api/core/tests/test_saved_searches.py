import os

import pytest
from rest_framework import status
from rest_framework.test import APIClient

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

import django

django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from core.models.busca_salva import BuscaSalva

SAVED_SEARCHES_ENDPOINT = "/api/saved-searches/"

pytestmark = pytest.mark.django_db


def _auth_client(email: str, password: str = "senha-segura-123") -> APIClient:
    user = User.objects.create_user(username=email, email=email, password=password)
    token = Token.objects.create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


class TestSavedSearchesPermissions:
    def test_given_no_token_when_list_then_returns_401(self):
        response = APIClient().get(SAVED_SEARCHES_ENDPOINT)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_given_no_token_when_create_then_returns_401(self):
        response = APIClient().post(
            SAVED_SEARCHES_ENDPOINT, {"title": "x", "query": "y"}, format="json"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestSavedSearchesCrud:
    def test_given_authenticated_user_when_create_then_associates_to_user(self):
        client = _auth_client("dono@example.com")

        response = client.post(
            SAVED_SEARCHES_ENDPOINT,
            {"title": "Escala 12x36", "query": "trabalhei 12h sem intervalo"},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Escala 12x36"

        busca = BuscaSalva.objects.get(id=data["id"])
        assert busca.user.email == "dono@example.com"

    def test_given_searches_from_two_users_when_list_then_returns_only_own(self):
        client_a = _auth_client("a@example.com")
        client_b = _auth_client("b@example.com")

        client_a.post(SAVED_SEARCHES_ENDPOINT, {"title": "A", "query": "qa"}, format="json")
        client_b.post(SAVED_SEARCHES_ENDPOINT, {"title": "B", "query": "qb"}, format="json")

        response = client_a.get(SAVED_SEARCHES_ENDPOINT)

        assert response.status_code == status.HTTP_200_OK
        titles = [item["title"] for item in response.json()["results"]]
        assert titles == ["A"]

    def test_given_owned_search_when_delete_then_removes_it(self):
        client = _auth_client("dono@example.com")
        created = client.post(
            SAVED_SEARCHES_ENDPOINT, {"title": "Apagar", "query": "q"}, format="json"
        ).json()

        response = client.delete(f"{SAVED_SEARCHES_ENDPOINT}{created['id']}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not BuscaSalva.objects.filter(id=created["id"]).exists()

    def test_given_other_users_search_when_delete_then_returns_404(self):
        client_a = _auth_client("a@example.com")
        client_b = _auth_client("b@example.com")
        created = client_a.post(
            SAVED_SEARCHES_ENDPOINT, {"title": "A", "query": "qa"}, format="json"
        ).json()

        response = client_b.delete(f"{SAVED_SEARCHES_ENDPOINT}{created['id']}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert BuscaSalva.objects.filter(id=created["id"]).exists()
