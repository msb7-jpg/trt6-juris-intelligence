import os
import unittest

from core.models.analise import Analise
from core.tests.constants import DATA_BASE, DETALHE_PROCESSO_ENDPOINT, PROCESSO_NUMERO_1, TRIBUNAL_TRT6
from core.tests.helpers import DataSetup

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

import django
import pytest
from rest_framework import status
from rest_framework.test import APIClient

django.setup()


pytestmark = pytest.mark.django_db


class TestProcessoViewsetDetalhe(unittest.TestCase):
    def test_given_existing_processo_when_get_detalhe_then_return_full_payload(self):
        api_client = APIClient()
        processo = DataSetup.create_processo_existente(
            numero_processo=PROCESSO_NUMERO_1,
            data_hora_ultima_atualizacao=DATA_BASE,
            tribunal=TRIBUNAL_TRT6,
            grau="G1",
            movimentos=[
                {
                    "codigo": 1,
                    "nome": "Distribuicao",
                    "data_hora": "2025-01-01T12:00:00-03:00",
                    "orgao_julgador": {
                        "codigo": 1001,
                        "nome": "1a Vara do Trabalho",
                    },
                }
            ],
        )
        processo.analise = Analise.objects.create(
            resumo="Resumo teste",
            decisao="Decisao teste",
            status="sentenciado",
        )
        processo.save(update_fields=["analise"])

        response = api_client.get(
            DETALHE_PROCESSO_ENDPOINT,
            {"numero_processo": PROCESSO_NUMERO_1, "grau": "1"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertEqual(body["numero_processo"], PROCESSO_NUMERO_1)
        self.assertEqual(body["movimentos"][0]["nome"], "Distribuicao")
        self.assertFalse(body["em_andamento"])

    def test_given_missing_processo_when_get_detalhe_then_return_404(self):
        api_client = APIClient()

        response = api_client.get(
            DETALHE_PROCESSO_ENDPOINT,
            {"numero_processo": PROCESSO_NUMERO_1, "grau": "1"},
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("mensagem", response.json())
